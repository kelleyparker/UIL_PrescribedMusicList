#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from pml_catalog_core import (
    INSTRUMENT_CONFIGS,
    affiliate_cache_path_for_instrument,
    load_affiliate_links_cache,
    read_rows_from_csv,
)


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


def ratio_line(label: str, numerator: int, denominator: int) -> str:
    percent = (numerator / denominator * 100.0) if denominator else 0.0
    return f"{label}: {numerator} / {denominator} ({percent:.2f}% complete)"


def main() -> int:
    total_records = 0
    attempted_records = 0
    linked_records = 0

    for instrument_slug, config in INSTRUMENT_CONFIGS.items():
        rows = read_rows_from_csv(config["csv_path"])
        total_records += len(rows)

        row_codes = {row.code for row in rows}
        affiliate_cache = load_affiliate_links_cache(affiliate_cache_path_for_instrument(instrument_slug))
        linked_codes = {code for code, entry in affiliate_cache.items() if isinstance(entry, dict) and entry.get("url")}

        attempt_codes = load_attempt_codes(instrument_slug)
        attempted_codes = (attempt_codes | set(affiliate_cache.keys())) & row_codes

        attempted_records += len(attempted_codes)
        linked_records += len(linked_codes & row_codes)

    print(ratio_line("Records attempted", attempted_records, total_records))
    print(ratio_line("Sheet music links obtained", linked_records, total_records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
