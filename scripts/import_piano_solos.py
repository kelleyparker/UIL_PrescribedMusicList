from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DATA_DIR = ROOT / "static" / "data"
SOURCE_CSV_PATH = ROOT / "data" / "uil_piano_solos_source.csv"
FRENCH_HORN_SOURCE_CSV_PATH = ROOT / "data" / "uil_french_horn_solos_source.csv"
TRUMPET_SOURCE_CSV_PATH = ROOT / "data" / "uil_trumpet_solos_source.csv"
DEFAULT_SCHOOL_YEAR = "2025-2026"
TAG_PATTERN = re.compile(r"<[^>]+>")
OPTION_PATTERN = re.compile(r"<option[^>]*>(.*?)</option>", re.IGNORECASE | re.DOTALL)

INSTRUMENT_CONFIGS = {
    "piano": {
        "event_name": "Piano Solo",
        "title": "Piano Solos",
        "csv_path": SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "piano-solos.json",
        "stats_output": STATIC_DATA_DIR / "piano-stats.json",
        "legacy_stats_output": STATIC_DATA_DIR / "stats.json",
    },
    "french-horn": {
        "event_name": "French Horn Solo",
        "title": "French Horn Solos",
        "csv_path": FRENCH_HORN_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "french-horn-solos.json",
        "stats_output": STATIC_DATA_DIR / "french-horn-stats.json",
    },
    "trumpet": {
        "event_name": "Cornet/Trumpet Solo",
        "title": "Trumpet Solos",
        "csv_path": TRUMPET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trumpet-solos.json",
        "stats_output": STATIC_DATA_DIR / "trumpet-stats.json",
    },
}


@dataclass
class SoloRow:
    code: str
    event_name: str
    title: str
    composer: str
    arranger: str
    publisher_text: str
    grade: int
    specification: str


PianoSoloRow = SoloRow


def normalize_publishers(raw_value: str) -> list[str]:
    if "<option" in (raw_value or "").lower():
        publishers = []
        for value in OPTION_PATTERN.findall(raw_value):
            cleaned = html.unescape(TAG_PATTERN.sub("", value)).strip()
            if cleaned and cleaned.lower() != "multiple publishers":
                publishers.append(cleaned)
        return publishers

    publishers = []
    for value in (raw_value or "").split(";"):
        cleaned = html.unescape(TAG_PATTERN.sub("", value)).strip()
        if cleaned:
            publishers.append(cleaned)
    return publishers


def clean_text(value: str) -> str:
    cleaned = html.unescape(TAG_PATTERN.sub("", value or "")).replace("\xa0", " ")
    return " ".join(cleaned.split())


def instrument_slug_for_event(event_name: str) -> str:
    normalized = clean_text(event_name).lower()
    for slug, config in INSTRUMENT_CONFIGS.items():
        if normalized == config["event_name"].lower():
            return slug
    slug = normalized.replace("&", "and").replace("/", " ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug.removesuffix("-solo")


def solo_row_to_dict(row: SoloRow) -> dict:
    publishers = normalize_publishers(row.publisher_text)
    clean_specification = clean_text(row.specification)
    instrument_slug = instrument_slug_for_event(row.event_name)
    return {
        "uilCode": row.code,
        "instrumentSlug": instrument_slug,
        "instrumentName": INSTRUMENT_CONFIGS.get(instrument_slug, {}).get(
            "title", clean_text(row.event_name)
        ),
        "eventName": row.event_name,
        "title": clean_text(row.title),
        "composer": clean_text(row.composer),
        "arranger": clean_text(row.arranger),
        "publishers": publishers,
        "publisherText": ";".join(publishers),
        "classLevel": row.grade,
        "specification": clean_specification,
        "noMemoryRequired": "NMR:" in clean_specification,
    }


def write_source_csv(rows: list[SoloRow], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "Code",
                "Event Name",
                "Title",
                "Composer",
                "Arranger",
                "Publisher [Collection]",
                "Grade",
                "Specification",
            ]
        )
        for row in rows:
            cleaned = solo_row_to_dict(row)
            writer.writerow(
                [
                    row.code,
                    row.event_name,
                    cleaned["title"],
                    cleaned["composer"],
                    cleaned["arranger"],
                    cleaned["publisherText"],
                    row.grade,
                    cleaned["specification"],
                ]
            )


def read_rows_from_csv(csv_path: Path) -> list[SoloRow]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            SoloRow(
                code=row["Code"].strip(),
                event_name=row["Event Name"].strip(),
                title=row["Title"].strip(),
                composer=row["Composer"].strip(),
                arranger=row["Arranger"].strip(),
                publisher_text=row["Publisher [Collection]"].strip(),
                grade=int(row["Grade"].strip()),
                specification=row["Specification"].strip(),
            )
            for row in reader
        ]


def dataset_note_rows(source_label: str) -> list[tuple[str, str]]:
    return [
        (
            "dataset_audit",
            (
                f"Sourced from {source_label}. "
                f"Imported {datetime.now(timezone.utc).isoformat()}."
            ),
        ),
    ]


def build_outputs(
    rows: list[SoloRow],
    *,
    school_year: str,
    source_label: str,
    instrument_slug: str,
    source_csv_path: Path | None = None,
    public_domain_links: dict[str, dict] | None = None,
) -> dict:
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    config = INSTRUMENT_CONFIGS[instrument_slug]
    songs_payload = []

    for row in rows:
        payload = solo_row_to_dict(row)
        link_info = (public_domain_links or {}).get(row.code, {})
        payload["publicDomainPdfUrl"] = link_info.get("pdfUrl")
        payload["publicDomainSource"] = link_info.get("source")
        songs_payload.append(payload)

    songs_payload.sort(
        key=lambda song: (-song["classLevel"], song["composer"], song["title"])
    )

    note_rows = dataset_note_rows(source_label)
    stats_payload = {
        "schoolYear": school_year,
        "instrumentSlug": instrument_slug,
        "instrumentName": config["title"],
        "songCount": len(songs_payload),
        "publisherCount": sum(len(song["publishers"]) for song in songs_payload),
        "noteCount": len(note_rows),
        "databaseRecordCount": len(songs_payload) + len(note_rows),
        "classBreakdown": {
            "3": sum(song["classLevel"] == 3 for song in songs_payload),
            "2": sum(song["classLevel"] == 2 for song in songs_payload),
            "1": sum(song["classLevel"] == 1 for song in songs_payload),
        },
        "noMemoryRequiredCount": sum(
            song["noMemoryRequired"] for song in songs_payload
        ),
        "publicDomainPdfCount": sum(
            bool(song["publicDomainPdfUrl"]) for song in songs_payload
        ),
        "notes": {key: value for key, value in note_rows},
    }

    config["songs_output"].write_text(
        json.dumps(songs_payload, indent=2), encoding="utf-8"
    )
    config["stats_output"].write_text(
        json.dumps(stats_payload, indent=2), encoding="utf-8"
    )

    legacy_stats_output = config.get("legacy_stats_output")
    if legacy_stats_output:
        legacy_stats_output.write_text(
            json.dumps(stats_payload, indent=2), encoding="utf-8"
        )

    if source_csv_path is not None:
        write_source_csv(rows, source_csv_path)

    return stats_payload


def build_from_csv(
    csv_path: Path = SOURCE_CSV_PATH,
    *,
    school_year: str = DEFAULT_SCHOOL_YEAR,
    source_label: str = "local CSV snapshot",
    instrument_slug: str = "piano",
    public_domain_links: dict[str, dict] | None = None,
) -> dict:
    rows = read_rows_from_csv(csv_path)
    return build_outputs(
        rows,
        school_year=school_year,
        source_label=source_label,
        instrument_slug=instrument_slug,
        source_csv_path=csv_path,
        public_domain_links=public_domain_links,
    )


def build_all_from_csv(
    *,
    school_year: str = DEFAULT_SCHOOL_YEAR,
    source_label: str = "local CSV snapshots",
    public_domain_links_by_instrument: dict[str, dict[str, dict]] | None = None,
) -> dict[str, dict]:
    outputs = {}
    for instrument_slug, config in INSTRUMENT_CONFIGS.items():
        csv_path = config["csv_path"]
        if not csv_path.exists():
            continue
        outputs[instrument_slug] = build_from_csv(
            csv_path,
            school_year=school_year,
            source_label=source_label,
            instrument_slug=instrument_slug,
            public_domain_links=(public_domain_links_by_instrument or {}).get(
                instrument_slug
            ),
        )
    return outputs


if __name__ == "__main__":
    build_all_from_csv()
