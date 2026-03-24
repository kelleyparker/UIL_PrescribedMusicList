from __future__ import annotations

import json
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts.import_piano_solos import DB_PATH, STATIC_DATA_DIR, build_from_csv


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


def ensure_database() -> None:
    if not DB_PATH.exists():
        build_from_csv()


def database_connection() -> sqlite3.Connection:
    ensure_database()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_piano_solos(search_term: str = "", class_filter: str = "all") -> list[dict]:
    sql = """
        SELECT
            piano_solos.id,
            piano_solos.uil_code,
            piano_solos.title,
            piano_solos.composer,
            piano_solos.arranger,
            piano_solos.publisher_text,
            piano_solos.class_level,
            piano_solos.specification,
            (
                SELECT GROUP_CONCAT(ordered_publishers.publisher_name, '||')
                FROM (
                    SELECT publisher_name
                    FROM publishers
                    WHERE publishers.piano_solo_id = piano_solos.id
                    ORDER BY sort_order
                ) AS ordered_publishers
            ) AS publishers
        FROM piano_solos
    """

    where_clauses = []
    parameters: list[str | int] = []

    if class_filter in {"1", "2", "3"}:
        where_clauses.append("piano_solos.class_level = ?")
        parameters.append(int(class_filter))
    elif class_filter == "nmr":
        where_clauses.append("piano_solos.specification LIKE ?")
        parameters.append("%NMR:%")

    if search_term:
        where_clauses.append(
            """
            (
                piano_solos.title LIKE ?
                OR piano_solos.composer LIKE ?
                OR piano_solos.publisher_text LIKE ?
            )
            """
        )
        search_value = f"%{search_term}%"
        parameters.extend([search_value, search_value, search_value])

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += """
        ORDER BY piano_solos.class_level DESC, piano_solos.composer ASC, piano_solos.title ASC
    """

    with database_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()

    payload = []
    for row in rows:
        publishers = row["publishers"].split("||") if row["publishers"] else []
        payload.append(
            {
                "id": row["id"],
                "uilCode": row["uil_code"],
                "title": row["title"],
                "composer": row["composer"],
                "arranger": row["arranger"],
                "publishers": publishers,
                "publisherText": row["publisher_text"],
                "classLevel": row["class_level"],
                "specification": row["specification"],
                "noMemoryRequired": "NMR:" in (row["specification"] or ""),
            }
        )

    return payload


def fetch_stats() -> dict:
    with database_connection() as connection:
        song_count = connection.execute("SELECT COUNT(*) FROM piano_solos").fetchone()[0]
        publisher_count = connection.execute(
            "SELECT COUNT(*) FROM publishers"
        ).fetchone()[0]
        note_count = connection.execute("SELECT COUNT(*) FROM dataset_notes").fetchone()[0]
        notes = connection.execute(
            "SELECT note_key, note_value FROM dataset_notes ORDER BY id"
        ).fetchall()
        classes = connection.execute(
            """
            SELECT class_level, COUNT(*) AS total
            FROM piano_solos
            GROUP BY class_level
            ORDER BY class_level DESC
            """
        ).fetchall()
        no_memory_required_count = connection.execute(
            "SELECT COUNT(*) FROM piano_solos WHERE specification LIKE '%NMR:%'"
        ).fetchone()[0]

    payload = {
        "songCount": song_count,
        "publisherCount": publisher_count,
        "noteCount": note_count,
        "databaseRecordCount": song_count + note_count,
        "classBreakdown": {str(row["class_level"]): row["total"] for row in classes},
        "noMemoryRequiredCount": no_memory_required_count,
        "notes": {row["note_key"]: row["note_value"] for row in notes},
    }

    stats_path = STATIC_DATA_DIR / "stats.json"
    if stats_path.exists():
        static_stats = json.loads(stats_path.read_text(encoding="utf-8"))
        payload["schoolYear"] = static_stats.get("schoolYear")

    return payload


class UILRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/piano-solos":
            self.handle_piano_solos(parsed_url.query)
            return

        if parsed_url.path == "/api/stats":
            self.handle_stats()
            return

        if parsed_url.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def handle_piano_solos(self, query_string: str) -> None:
        query = parse_qs(query_string)
        search_term = (query.get("q", [""])[0] or "").strip()
        class_filter = (query.get("class", ["all"])[0] or "all").strip()
        self.send_json(fetch_piano_solos(search_term=search_term, class_filter=class_filter))

    def handle_stats(self) -> None:
        self.send_json(fetch_stats())

    def send_json(self, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    ensure_database()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), UILRequestHandler)
    print("Serving UIL Piano Solos at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
