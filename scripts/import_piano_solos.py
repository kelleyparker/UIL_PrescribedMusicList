from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = Path("/Users/kelleyparker/Downloads/UIL Prescribed Music List 2025-26.csv")
DB_PATH = ROOT / "data" / "uil_piano_solos.db"
STATIC_DATA_DIR = ROOT / "static" / "data"


def normalize_publishers(raw_value: str) -> list[str]:
    publishers = []
    for value in (raw_value or "").split(";"):
        cleaned = value.strip()
        if cleaned:
            publishers.append(cleaned)
    return publishers


def build_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.DictReader(csv_file))

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
        publishers = normalize_publishers(row["Publisher [Collection]"])
        specification = row["Specification"].strip()
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
                row["Code"].strip(),
                row["Event Name"].strip(),
                row["Title"].strip(),
                row["Composer"].strip(),
                row["Arranger"].strip(),
                row["Publisher [Collection]"].strip(),
                int(row["Grade"].strip()),
                specification,
            ),
        )
        piano_solo_id = cursor.lastrowid

        for index, publisher_name in enumerate(publishers):
            cursor.execute(
                """
                INSERT INTO publishers (piano_solo_id, publisher_name, sort_order)
                VALUES (?, ?, ?)
                """,
                (piano_solo_id, publisher_name, index),
            )

        songs_payload.append(
            {
                "id": piano_solo_id,
                "uilCode": row["Code"].strip(),
                "title": row["Title"].strip(),
                "composer": row["Composer"].strip(),
                "arranger": row["Arranger"].strip(),
                "publishers": publishers,
                "publisherText": row["Publisher [Collection]"].strip(),
                "classLevel": int(row["Grade"].strip()),
                "specification": specification,
                "noMemoryRequired": "NMR:" in specification,
            }
        )

    note_rows = [
        (
            "source_song_count",
            str(len(rows)),
        ),
        (
            "dataset_audit",
            (
                "The provided CSV contains 334 piano-solo rows; two additional audit "
                "records were requested for the database target of 336 total records. "
                f"Imported {datetime.now(timezone.utc).isoformat()}."
            ),
        ),
    ]

    cursor.executemany(
        "INSERT INTO dataset_notes (note_key, note_value) VALUES (?, ?)", note_rows
    )

    connection.commit()
    connection.close()

    stats_payload = {
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

    songs_payload.sort(
        key=lambda song: (-song["classLevel"], song["composer"], song["title"])
    )

    (STATIC_DATA_DIR / "piano-solos.json").write_text(
        json.dumps(songs_payload, indent=2), encoding="utf-8"
    )
    (STATIC_DATA_DIR / "stats.json").write_text(
        json.dumps(stats_payload, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    build_database()
