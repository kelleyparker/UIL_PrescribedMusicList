from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts.import_piano_solos import STATIC_DATA_DIR, build_all_from_csv


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
INSTRUMENT_FILES = {
    "piano": {
        "songs": STATIC_DATA_DIR / "piano-solos.json",
        "stats": STATIC_DATA_DIR / "piano-stats.json",
    },
    "french-horn": {
        "songs": STATIC_DATA_DIR / "french-horn-solos.json",
        "stats": STATIC_DATA_DIR / "french-horn-stats.json",
    },
    "trumpet": {
        "songs": STATIC_DATA_DIR / "trumpet-solos.json",
        "stats": STATIC_DATA_DIR / "trumpet-stats.json",
    },
}


def ensure_static_data() -> None:
    missing_outputs = [
        path
        for files in INSTRUMENT_FILES.values()
        for path in files.values()
        if not path.exists()
    ]
    if missing_outputs:
        build_all_from_csv()


def load_dataset(instrument_slug: str) -> tuple[list[dict], dict]:
    ensure_static_data()
    files = INSTRUMENT_FILES.get(instrument_slug, INSTRUMENT_FILES["piano"])
    songs = json.loads(files["songs"].read_text(encoding="utf-8"))
    stats = json.loads(files["stats"].read_text(encoding="utf-8"))
    return songs, stats


def fetch_solos(
    instrument_slug: str = "piano",
    search_term: str = "",
    class_filter: str = "all",
) -> list[dict]:
    songs, _ = load_dataset(instrument_slug)
    filtered = []
    lowered_query = search_term.lower()

    for song in songs:
        filter_matches = (
            class_filter == "all"
            or (class_filter == "nmr" and song["noMemoryRequired"])
            or str(song["classLevel"]) == class_filter
        )
        if not filter_matches:
            continue

        search_matches = (
            not lowered_query
            or lowered_query in song["title"].lower()
            or lowered_query in song["composer"].lower()
            or lowered_query in song["publisherText"].lower()
        )
        if search_matches:
            filtered.append(song)

    return filtered


def fetch_stats(instrument_slug: str = "piano") -> dict:
    _, stats = load_dataset(instrument_slug)
    return stats


class UILRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/solos":
            self.handle_solos(parsed_url.query)
            return

        if parsed_url.path == "/api/stats":
            self.handle_stats(parsed_url.query)
            return

        if parsed_url.path == "/api/piano-solos":
            self.handle_solos(parsed_url.query, instrument_slug="piano")
            return

        if parsed_url.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def handle_solos(
        self,
        query_string: str,
        *,
        instrument_slug: str | None = None,
    ) -> None:
        query = parse_qs(query_string)
        search_term = (query.get("q", [""])[0] or "").strip()
        class_filter = (query.get("class", ["all"])[0] or "all").strip()
        instrument = instrument_slug or (query.get("instrument", ["piano"])[0] or "piano")
        self.send_json(
            fetch_solos(
                instrument_slug=instrument,
                search_term=search_term,
                class_filter=class_filter,
            )
        )

    def handle_stats(self, query_string: str) -> None:
        query = parse_qs(query_string)
        instrument = (query.get("instrument", ["piano"])[0] or "piano").strip()
        self.send_json(fetch_stats(instrument))

    def send_json(self, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    ensure_static_data()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), UILRequestHandler)
    print("Serving UIL Prescribed Music List at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
