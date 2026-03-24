from __future__ import annotations

import csv
import html
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "uil_piano_solos.db"
STATIC_DATA_DIR = ROOT / "static" / "data"
SOURCE_CSV_PATH = ROOT / "data" / "uil_piano_solos_source.csv"
DEFAULT_SCHOOL_YEAR = "2025-2026"
TAG_PATTERN = re.compile(r"<[^>]+>")
OPTION_PATTERN = re.compile(r"<option[^>]*>(.*?)</option>", re.IGNORECASE | re.DOTALL)


@dataclass
class PianoSoloRow:
    code: str
    event_name: str
    title: str
    composer: str
    arranger: str
    publisher_text: str
    grade: int
    specification: str


def normalize_publishers(raw_value: str) -> list[str]:
    if "<option" in (raw_value or "").lower():
        publishers = []
        for value in OPTION_PATTERN.findall(raw_value):
            cleaned = html.unescape(TAG_PATTERN.sub("", value)).strip()
            if cleaned:
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


def piano_row_to_dict(row: PianoSoloRow) -> dict:
    publishers = normalize_publishers(row.publisher_text)
    return {
        "uilCode": row.code,
        "eventName": row.event_name,
        "title": clean_text(row.title),
        "composer": clean_text(row.composer),
        "arranger": clean_text(row.arranger),
        "publishers": publishers,
        "publisherText": ";".join(publishers),
        "classLevel": row.grade,
        "specification": clean_text(row.specification),
        "noMemoryRequired": "NMR:" in clean_text(row.specification),
    }


def write_source_csv(rows: list[PianoSoloRow], destination: Path) -> None:
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
            cleaned = piano_row_to_dict(row)
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


def read_rows_from_csv(csv_path: Path) -> list[PianoSoloRow]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            PianoSoloRow(
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


def build_outputs(
    rows: list[PianoSoloRow],
    *,
    school_year: str,
    source_label: str,
    source_csv_path: Path | None = None,
) -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.executescript(
        """
        DROP TABLE IF EXISTS publishers;
        DROP TABLE IF EXISTS piano_solos;
        DROP TABLE IF EXISTS dataset_notes;

        CREATE TABLE piano_solos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uil_code TEXT NOT NULL UNIQUE,
            event_name TEXT NOT NULL,
            title TEXT NOT NULL,
            composer TEXT NOT NULL,
            arranger TEXT,
            publisher_text TEXT NOT NULL,
            class_level INTEGER NOT NULL,
            specification TEXT,
            source_type TEXT NOT NULL DEFAULT 'uil'
        );

        CREATE TABLE publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piano_solo_id INTEGER NOT NULL,
            publisher_name TEXT NOT NULL,
            sort_order INTEGER NOT NULL,
            FOREIGN KEY (piano_solo_id) REFERENCES piano_solos(id)
        );

        CREATE TABLE dataset_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_key TEXT NOT NULL UNIQUE,
            note_value TEXT NOT NULL
        );
        """
    )

    songs_payload = []

    for row in rows:
        payload = piano_row_to_dict(row)
        cursor.execute(
            """
            INSERT INTO piano_solos (
                uil_code,
                event_name,
                title,
                composer,
                arranger,
                publisher_text,
                class_level,
                specification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.code,
                row.event_name,
                clean_text(row.title),
                clean_text(row.composer),
                clean_text(row.arranger),
                ";".join(payload["publishers"]),
                row.grade,
                payload["specification"],
            ),
        )
        piano_solo_id = cursor.lastrowid

        for index, publisher_name in enumerate(payload["publishers"]):
            cursor.execute(
                """
                INSERT INTO publishers (piano_solo_id, publisher_name, sort_order)
                VALUES (?, ?, ?)
                """,
                (piano_solo_id, publisher_name, index),
            )

        payload["id"] = piano_solo_id
        songs_payload.append(payload)

    note_rows = [
        ("source_song_count", str(len(rows))),
        (
            "dataset_audit",
            (
                f"Sourced from {source_label}. "
                f"Imported {datetime.now(timezone.utc).isoformat()}."
            ),
        ),
    ]

    cursor.executemany(
        "INSERT INTO dataset_notes (note_key, note_value) VALUES (?, ?)", note_rows
    )

    connection.commit()
    connection.close()

    songs_payload.sort(
        key=lambda song: (-song["classLevel"], song["composer"], song["title"])
    )

    stats_payload = {
        "schoolYear": school_year,
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
        "notes": {key: value for key, value in note_rows},
    }

    (STATIC_DATA_DIR / "piano-solos.json").write_text(
        json.dumps(songs_payload, indent=2), encoding="utf-8"
    )
    (STATIC_DATA_DIR / "stats.json").write_text(
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
) -> dict:
    rows = read_rows_from_csv(csv_path)
    return build_outputs(
        rows,
        school_year=school_year,
        source_label=source_label,
        source_csv_path=csv_path,
    )


if __name__ == "__main__":
    build_from_csv()
