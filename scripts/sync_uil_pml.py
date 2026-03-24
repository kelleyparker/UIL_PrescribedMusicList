from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_piano_solos import SOURCE_CSV_PATH, PianoSoloRow, build_outputs


ROOT = Path(__file__).resolve().parents[1]
UIL_HOME = "https://www.uiltexas.org/pml/"
UIL_DATA = "https://www.uiltexas.org/pml/pml.php"
YEAR_PATTERN = re.compile(r"(20\d{2}-20\d{2})\s+Prescribed Music List")


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-Piano-Solos-Sync/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "UIL-Piano-Solos-Sync/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def detect_school_year(homepage_html: str) -> str:
    match = YEAR_PATTERN.search(homepage_html)
    if not match:
        raise RuntimeError("Could not detect UIL school year from homepage.")
    return match.group(1)


def fetch_piano_solo_rows() -> list[PianoSoloRow]:
    payload = fetch_json(UIL_DATA)
    rows = []
    for entry in payload["pml"]:
        if len(entry) < 8 or entry[1].strip() != "Piano Solo":
            continue
        rows.append(
            PianoSoloRow(
                code=entry[0].strip(),
                event_name=entry[1].strip(),
                title=entry[2].strip(),
                composer=entry[3].strip(),
                arranger=entry[4].strip(),
                publisher_text=entry[5].strip(),
                grade=int(entry[6].strip()),
                specification=entry[7].strip(),
            )
        )
    return rows


def main() -> int:
    homepage_html = fetch_text(UIL_HOME)
    school_year = detect_school_year(homepage_html)
    piano_solo_rows = fetch_piano_solo_rows()

    stats = build_outputs(
        piano_solo_rows,
        school_year=school_year,
        source_label=f"{UIL_HOME} and {UIL_DATA}",
        source_csv_path=SOURCE_CSV_PATH,
    )

    print(
        json.dumps(
            {
                "schoolYear": school_year,
                "songCount": stats["songCount"],
                "noMemoryRequiredCount": stats["noMemoryRequiredCount"],
                "databaseRecordCount": stats["databaseRecordCount"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
