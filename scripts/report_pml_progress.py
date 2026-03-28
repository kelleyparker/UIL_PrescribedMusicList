#!/usr/bin/env python3

from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from pml_catalog_core import (
    INSTRUMENT_CONFIGS,
    affiliate_cache_path_for_instrument,
    load_affiliate_links_cache,
    read_rows_from_csv,
)


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "logs" / "scan_full_catalog_status.json"
LOG_PATH = ROOT / "logs" / "fill_sheet_music_links.log"
REPORT_STATE_PATH = ROOT / "logs" / "report_pml_progress_state.json"
ACTIVE_WRITE_WINDOW_SECONDS = int(os.getenv("SCAN_ACTIVE_WRITE_WINDOW_SECONDS", "180"))
ETA_SAMPLE_MIN_SECONDS = float(os.getenv("SCAN_ETA_SAMPLE_MIN_SECONDS", "15"))


def attempt_cache_paths(instrument_slug: str) -> list[Path]:
    affiliate_cache_path = affiliate_cache_path_for_instrument(instrument_slug)
    data_dir = affiliate_cache_path.parent
    return [
        data_dir / f"{instrument_slug}_attempts.json",
        data_dir / f"{instrument_slug}_affiliate_attempts.json",
    ]


def load_attempt_codes(instrument_slug: str) -> set[str]:
    codes: set[str] = set()
    for cache_path in attempt_cache_paths(instrument_slug):
        if not cache_path.exists():
            continue
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(payload, dict):
            codes.update(str(code) for code in payload.keys() if code)
        elif isinstance(payload, list):
            codes.update(str(code) for code in payload if code)

    return codes


def render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    def format_row(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(values)) + " |"

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = [separator, format_row(headers), separator]
    for row in rows:
        lines.append(format_row(row))
    lines.append(separator)
    return lines


def site_from_url(url: str) -> str:
    if not url:
        return "unknown"
    try:
        host = (urlparse(url).netloc or "").lower()
    except Exception:
        return "unknown"
    if host.startswith("www."):
        host = host[4:]
    return host or "unknown"


def is_recently_written(path: Path, now_epoch: float, window_seconds: int) -> bool:
    try:
        return path.exists() and (now_epoch - path.stat().st_mtime) <= window_seconds
    except OSError:
        return False


def infer_active_instruments_from_writes(window_seconds: int) -> list[str]:
    now_epoch = time.time()
    active: list[str] = []
    for instrument_slug in sorted(INSTRUMENT_CONFIGS):
        paths = [affiliate_cache_path_for_instrument(instrument_slug), *attempt_cache_paths(instrument_slug)]
        if any(is_recently_written(path, now_epoch, window_seconds) for path in paths):
            active.append(instrument_slug)
    return active


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def parse_iso_timestamp(value: str) -> float | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def load_status_payload() -> dict:
    if not STATUS_PATH.exists():
        return {}
    try:
        payload = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def active_scan_state() -> tuple[str, bool]:
    payload = load_status_payload()
    if payload:
        pid = int(payload.get("pid") or 0)
        phase = str(payload.get("phase") or "")
        active_instruments = payload.get("activeInstruments") or []
        if not isinstance(active_instruments, list):
            active_instruments = []

        if phase == "running" and process_is_alive(pid):
            if active_instruments:
                return (
                    f"Active scan instruments: {', '.join(sorted(str(v) for v in active_instruments))}",
                    True,
                )
            return ("Active scan instruments: initializing", True)

    inferred_active = infer_active_instruments_from_writes(ACTIVE_WRITE_WINDOW_SECONDS)
    if inferred_active:
        return (
            "Active scan instruments (inferred): " + ", ".join(inferred_active),
            True,
        )

    now_epoch = time.time()
    if is_recently_written(LOG_PATH, now_epoch, ACTIVE_WRITE_WINDOW_SECONDS):
        return ("Active scan instruments: scan activity detected (instrument unknown)", True)

    return ("Active scan instruments: none detected", False)


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def load_previous_report_state() -> dict:
    if not REPORT_STATE_PATH.exists():
        return {}
    try:
        payload = json.loads(REPORT_STATE_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def save_report_state(now_epoch: float, attempted_records: int, total_records: int) -> None:
    prev = load_previous_report_state()
    prev_time = float(prev.get("observedAt") or 0)
    # Keep a wider sampling window so watch-refresh runs do not constantly reset ETA baseline.
    if prev_time > 0 and (now_epoch - prev_time) < ETA_SAMPLE_MIN_SECONDS:
        return

    payload = {
        "observedAt": now_epoch,
        "attemptedRecords": attempted_records,
        "totalRecords": total_records,
    }
    REPORT_STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def estimate_eta_text(*, attempted_records: int, total_records: int, scan_active: bool) -> str:
    if total_records <= 0:
        return "n/a"
    if attempted_records >= total_records:
        return "complete"
    if not scan_active:
        return "n/a (scan not active)"

    now_epoch = time.time()
    remaining = total_records - attempted_records
    candidates: list[float] = []

    prev = load_previous_report_state()
    prev_attempted = int(prev.get("attemptedRecords") or 0)
    prev_time = float(prev.get("observedAt") or 0)
    if prev_time > 0 and now_epoch > prev_time and attempted_records > prev_attempted:
        elapsed = now_epoch - prev_time
        gained = attempted_records - prev_attempted
        if elapsed >= 5 and gained > 0:
            candidates.append(gained / elapsed)

    status_payload = load_status_payload()
    started_at_epoch = parse_iso_timestamp(str(status_payload.get("startedAt") or ""))
    if started_at_epoch and now_epoch > started_at_epoch and attempted_records > 0:
        elapsed = now_epoch - started_at_epoch
        if elapsed >= 30:
            candidates.append(attempted_records / elapsed)

    chosen_rate = max(candidates) if candidates else 0.0
    if chosen_rate <= 0:
        return "estimating..."

    eta_seconds = remaining / chosen_rate
    rate_per_min = chosen_rate * 60.0
    return f"{format_duration(eta_seconds)} remaining @ ~{rate_per_min:.1f} attempted/min"


def main() -> int:
    total_records = 0
    attempted_records = 0
    linked_records = 0
    per_category: list[tuple[str, int, int, int]] = []
    linked_sites: Counter[str] = Counter()

    active_message, scan_active = active_scan_state()
    print(active_message)

    for instrument_slug, config in INSTRUMENT_CONFIGS.items():
        rows = read_rows_from_csv(config["csv_path"])
        total_records += len(rows)

        row_codes = {row.code for row in rows}
        affiliate_cache = load_affiliate_links_cache(affiliate_cache_path_for_instrument(instrument_slug))
        linked_codes = set()
        for code, entry in affiliate_cache.items():
            if not isinstance(entry, dict):
                continue
            url = str(entry.get("url") or "")
            if not url or code not in row_codes:
                continue
            linked_codes.add(code)
            linked_sites[site_from_url(url)] += 1

        attempt_codes = load_attempt_codes(instrument_slug)
        attempted_codes = (attempt_codes | set(affiliate_cache.keys())) & row_codes

        attempted_records += len(attempted_codes)
        linked_records += len(linked_codes & row_codes)
        per_category.append((instrument_slug, len(rows), len(attempted_codes), len(linked_codes & row_codes)))

    eta_text = estimate_eta_text(
        attempted_records=attempted_records,
        total_records=total_records,
        scan_active=scan_active,
    )

    summary_rows = [
        [
            "Records attempted",
            str(attempted_records),
            str(total_records),
            f"{(attempted_records / total_records * 100.0) if total_records else 0.0:.2f}%",
        ],
        [
            "Sheet music links obtained",
            str(linked_records),
            str(total_records),
            f"{(linked_records / total_records * 100.0) if total_records else 0.0:.2f}%",
        ],
        [
            "ETA to 100% attempted",
            eta_text,
            "",
            "",
        ],
    ]

    save_report_state(time.time(), attempted_records, total_records)

    print(f"Categories tracked: {len(INSTRUMENT_CONFIGS)}")
    for line in render_table(["Metric", "Count", "Total", "% Complete"], summary_rows):
        print(line)

    in_progress: list[tuple[str, int, int, int]] = []
    scan_complete: list[tuple[str, int, int, int]] = []
    for row in sorted(per_category):
        instrument_slug, total, attempted, linked = row
        if total > 0 and attempted == total:
            scan_complete.append(row)
        else:
            in_progress.append(row)

    print()
    print("In-progress categories (scan < 100% attempted):")
    in_progress_rows: list[list[str]] = []
    for instrument_slug, total, attempted, linked in in_progress:
        attempted_pct = (attempted / total * 100.0) if total else 0.0
        linked_pct = (linked / total * 100.0) if total else 0.0
        in_progress_rows.append(
            [
                instrument_slug,
                str(attempted),
                str(total),
                f"{attempted_pct:.2f}%",
                str(linked),
                f"{linked_pct:.2f}%",
            ]
        )
    for line in render_table(
        ["Category", "Attempted", "Total", "Attempted %", "Links", "Links %"],
        in_progress_rows,
    ):
        print(line)

    print()
    print()
    print("100% scan-complete categories:")
    complete_rows: list[list[str]] = []
    for instrument_slug, total, attempted, linked in scan_complete:
        attempted_pct = (attempted / total * 100.0) if total else 0.0
        linked_pct = (linked / total * 100.0) if total else 0.0
        complete_rows.append(
            [
                instrument_slug,
                str(attempted),
                str(total),
                f"{attempted_pct:.2f}%",
                str(linked),
                f"{linked_pct:.2f}%",
            ]
        )
    for line in render_table(
        ["Category", "Attempted", "Total", "Attempted %", "Links", "Links %"],
        complete_rows,
    ):
        print(line)

    print()
    print()
    print("Found links by site:")
    site_rows: list[list[str]] = []
    for site, count in linked_sites.most_common():
        found_pct = (count / linked_records * 100.0) if linked_records else 0.0
        site_rows.append([site, str(count), f"{found_pct:.2f}%"])
    for line in render_table(["Site", "Found Links", "% Of Found Links"], site_rows):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
