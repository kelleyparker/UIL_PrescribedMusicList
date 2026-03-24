from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_piano_solos import (
    FRENCH_HORN_SOURCE_CSV_PATH,
    SOURCE_CSV_PATH,
    INSTRUMENT_CONFIGS,
    PianoSoloRow,
    TRUMPET_SOURCE_CSV_PATH,
    build_outputs,
)
from public_domain_links import enrich_public_domain_links


ROOT = Path(__file__).resolve().parents[1]
UIL_HOME = "https://www.uiltexas.org/pml/"
UIL_DATA = "https://www.uiltexas.org/pml/pml.php"
YEAR_PATTERN = re.compile(r"(20\d{2}-20\d{2})\s+Prescribed Music List")
CSV_PATHS = {
    "piano": SOURCE_CSV_PATH,
    "french-horn": FRENCH_HORN_SOURCE_CSV_PATH,
    "trumpet": TRUMPET_SOURCE_CSV_PATH,
}
TRUMPET_LINKS_CACHE_PATH = ROOT / "data" / "trumpet_public_domain_links.json"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-PML-Sync/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-PML-Sync/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def detect_school_year(homepage_html: str) -> str:
    match = YEAR_PATTERN.search(homepage_html)
    if not match:
        raise RuntimeError("Could not detect UIL school year from homepage.")
    return match.group(1)


def fetch_rows_for_event(event_name: str) -> list[PianoSoloRow]:
    payload = fetch_json(UIL_DATA)
    rows = []
    for entry in payload["pml"]:
        normalized = [(value or "") if not isinstance(value, str) else value for value in entry]
        if len(normalized) < 8 or normalized[1].strip() != event_name:
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


def main() -> int:
    homepage_html = fetch_text(UIL_HOME)
    school_year = detect_school_year(homepage_html)

    rows_by_instrument = {
        instrument_slug: fetch_rows_for_event(config["event_name"])
        for instrument_slug, config in INSTRUMENT_CONFIGS.items()
    }

    public_domain_links_by_instrument = {
        "piano": {},
        "french-horn": enrich_public_domain_links(rows_by_instrument["french-horn"]),
        "trumpet": enrich_public_domain_links(
            rows_by_instrument["trumpet"],
            cache_path=TRUMPET_LINKS_CACHE_PATH,
        ),
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
