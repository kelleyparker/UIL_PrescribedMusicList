from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_piano_solos import (
    ALTO_SAXOPHONE_SOURCE_CSV_PATH,
    BASSOON_SOURCE_CSV_PATH,
    CLARINET_SOURCE_CSV_PATH,
    FRENCH_HORN_SOURCE_CSV_PATH,
    FLUTE_SOURCE_CSV_PATH,
    INSTRUMENT_CONFIGS,
    OBOE_SOURCE_CSV_PATH,
    PianoSoloRow,
    SAXOPHONE_SOURCE_CSV_PATH,
    SOURCE_CSV_PATH,
    TROMBONE_SOURCE_CSV_PATH,
    TRUMPET_SOURCE_CSV_PATH,
    TUBA_SOURCE_CSV_PATH,
    build_outputs,
)
from public_domain_links import enrich_public_domain_links, load_cache, song_key


ROOT = Path(__file__).resolve().parents[1]
UIL_HOME = "https://www.uiltexas.org/pml/"
UIL_DATA = "https://www.uiltexas.org/pml/pml.php"
YEAR_PATTERN = re.compile(r"(20\d{2}-20\d{2})\s+Prescribed Music List")
CSV_PATHS = {
    "piano": SOURCE_CSV_PATH,
    "clarinet": CLARINET_SOURCE_CSV_PATH,
    "french-horn": FRENCH_HORN_SOURCE_CSV_PATH,
    "saxophone": SAXOPHONE_SOURCE_CSV_PATH,
    "trombone": TROMBONE_SOURCE_CSV_PATH,
    "trumpet": TRUMPET_SOURCE_CSV_PATH,
    "tuba": TUBA_SOURCE_CSV_PATH,
    "flute": FLUTE_SOURCE_CSV_PATH,
    "oboe": OBOE_SOURCE_CSV_PATH,
    "bassoon": BASSOON_SOURCE_CSV_PATH,
    "alto-saxophone": ALTO_SAXOPHONE_SOURCE_CSV_PATH,
}
CLARINET_LINKS_CACHE_PATH = ROOT / "data" / "clarinet_public_domain_links.json"
TRUMPET_LINKS_CACHE_PATH = ROOT / "data" / "trumpet_public_domain_links.json"

def fetch_with_curl(url: str) -> str:
    result = subprocess.run(
        ["curl", "-fsSL", "-A", "UIL-PML-Sync/1.0", url],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-PML-Sync/1.0"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8", "ignore")
    except urllib.error.URLError:
        return fetch_with_curl(url)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-PML-Sync/1.0"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.URLError:
        return json.loads(fetch_with_curl(url))


def detect_school_year(homepage_html: str) -> str:
    match = YEAR_PATTERN.search(homepage_html)
    if not match:
        raise RuntimeError("Could not detect UIL school year from homepage.")
    return match.group(1)


def fetch_rows_for_events(event_names: list[str]) -> list[PianoSoloRow]:
    payload = fetch_json(UIL_DATA)
    rows = []
    allowed_event_names = {name.strip() for name in event_names}
    for entry in payload["pml"]:
        normalized = [(value or "") if not isinstance(value, str) else value for value in entry]
        if len(normalized) < 8 or normalized[1].strip() not in allowed_event_names:
            continue
        rows.append(
            PianoSoloRow(
                code=normalized[0].strip(),
                event_name=normalized[1].strip(),
                title=normalized[2].strip(),
                composer=normalized[3].strip(),
                arranger=normalized[4].strip(),
                publisher_text=normalized[5].strip(),
                grade=int(str(normalized[6]).strip()),
                specification=normalized[7].strip(),
            )
        )
    return rows


def load_clarinet_links(rows: list[PianoSoloRow]) -> dict[str, dict]:
    cache = load_cache(CLARINET_LINKS_CACHE_PATH)
    return {
        row.code: cache[f"{row.event_name}::{row.composer}::{row.title}"]
        for row in rows
        if f"{row.event_name}::{row.composer}::{row.title}" in cache
    }


def main() -> int:
    homepage_html = fetch_text(UIL_HOME)
    school_year = detect_school_year(homepage_html)

    rows_by_instrument = {
        instrument_slug: fetch_rows_for_events(
            config.get("event_names", [config["event_name"]])
        )
        for instrument_slug, config in INSTRUMENT_CONFIGS.items()
    }

    public_domain_links_by_instrument = {
        "piano": {
            row.code: cached
            for row in rows_by_instrument["piano"]
            if (cached := load_cache().get(song_key(row)))
        },
        "clarinet": load_clarinet_links(rows_by_instrument["clarinet"]),
        "french-horn": enrich_public_domain_links(rows_by_instrument["french-horn"]),
        "trumpet": enrich_public_domain_links(
            rows_by_instrument["trumpet"],
            cache_path=TRUMPET_LINKS_CACHE_PATH,
        ),
        "saxophone": {},
        "trombone": {},
        "tuba": {},
        "flute": {},
        "oboe": {},
        "bassoon": {},
        "alto-saxophone": {},
    }

    stats_by_instrument = {}
    for instrument_slug, rows in rows_by_instrument.items():
        stats_by_instrument[instrument_slug] = build_outputs(
            rows,
            school_year=school_year,
            source_label=f"{UIL_HOME} and {UIL_DATA}",
            instrument_slug=instrument_slug,
            source_csv_path=CSV_PATHS[instrument_slug],
            public_domain_links=public_domain_links_by_instrument.get(instrument_slug),
        )

    print(
        json.dumps(
            {
                instrument_slug: {
                    "schoolYear": school_year,
                    "songCount": stats["songCount"],
                    "noMemoryRequiredCount": stats["noMemoryRequiredCount"],
                    "publicDomainPdfCount": stats["publicDomainPdfCount"],
                }
                for instrument_slug, stats in stats_by_instrument.items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
