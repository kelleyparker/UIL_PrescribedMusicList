from __future__ import annotations

import csv
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_piano_solos import TAG_PATTERN, clean_text, normalize_publishers


ROOT = Path(__file__).resolve().parents[1]
UIL_HOME = "https://www.uiltexas.org/pml/"
UIL_DATA = "https://www.uiltexas.org/pml/pml.php"
STATIC_DATA_DIR = ROOT / "static" / "data"
SOURCE_CSV_PATH = ROOT / "data" / "uil_clarinet_solos_source.csv"
PUBLIC_DOMAIN_CACHE_PATH = ROOT / "data" / "clarinet_public_domain_links.json"
CLARINET_SONGS_PATH = STATIC_DATA_DIR / "clarinet-solos.json"
CLARINET_STATS_PATH = STATIC_DATA_DIR / "clarinet-stats.json"
DEFAULT_SCHOOL_YEAR = "2025-2026"
YEAR_PATTERN = re.compile(r"(20\d{2}-20\d{2})\s+Prescribed Music List")
DDG_SEARCH_URL = "https://duckduckgo.com/html/?q="
IMSLP_BLOCK_PATTERN = re.compile(
    r'<div id="IMSLP(\d+)" class="we_file(?:_first)? we_fileblock_[^"]+">(.*?)<div class="we_clear"></div>\s*</div>',
    re.DOTALL,
)
IMSLP_PDF_PATTERN = re.compile(r'href="(/images/[^"]+\.pdf)"')
IMSLP_TITLE_PATTERN = re.compile(r"Special:ImagefromIndex/\d+[^>]*>(.*?)</a></b>", re.DOTALL)
IMSLP_INDEX_GROUP_PATTERN = re.compile(r"indexes=([0-9/]+)")
DDG_RESULT_PATTERN = re.compile(r'class="result__a" href="([^"]+)"')
KNOWN_IMSLP_PAGES = {
    "207-1-10730": "https://imslp.org/wiki/Clarinet_Sonata_No.1,_Op.120_No.1_(Brahms,_Johannes)",
    "207-1-10822": "https://imslp.org/wiki/Clarinet_Sonata_No.2,_Op.120_No.2_(Brahms,_Johannes)",
    "207-2-24166": "https://imslp.org/wiki/Clarinet_Sonata_No.2,_Op.120_No.2_(Brahms,_Johannes)",
    "207-1-10732": "https://imslp.org/wiki/Adagio_e_Tarantella_(Cavallini,_Ernesto)",
    "207-1-10741": "https://imslp.org/wiki/Premi%C3%A8re_rhapsodie_(Debussy,_Claude)",
    "207-1-10767": "https://imslp.org/wiki/Clarinet_Concerto_in_A_major,_K.622_(Mozart,_Wolfgang_Amadeus)",
    "207-1-10781": "https://imslp.org/wiki/Sonata_for_Clarinet_and_Piano,_Op.167_(Saint-Sa%C3%ABns,_Camille)",
    "207-2-10866": "https://imslp.org/wiki/Sonata_for_Clarinet_and_Piano,_Op.167_(Saint-Sa%C3%ABns,_Camille)",
    "207-1-10783": "https://imslp.org/wiki/Fantasiest%C3%BCcke,_Op.73_(Schumann,_Robert)",
    "207-2-10867": "https://imslp.org/wiki/Fantasiest%C3%BCcke,_Op.73_(Schumann,_Robert)",
    "207-1-10802": "https://imslp.org/wiki/Clarinet_Concertino,_Op.26_(Weber,_Carl_Maria_von)",
    "207-1-10804": "https://imslp.org/wiki/Clarinet_Concerto_No.1,_Op.73_(Weber,_Carl_Maria_von)",
    "207-2-24162": "https://imslp.org/wiki/Clarinet_Concerto_No.1,_Op.73_(Weber,_Carl_Maria_von)",
    "207-1-10805": "https://imslp.org/wiki/Grand_Duo_Concertant,_Op.48_(Weber,_Carl_Maria_von)",
    "207-2-24163": "https://imslp.org/wiki/Grand_Duo_Concertant,_Op.48_(Weber,_Carl_Maria_von)",
    "207-1-10810": "https://imslp.org/wiki/Clarinet_Concerto_No.2,_Op.74_(Weber,_Carl_Maria_von)",
    "207-2-24165": "https://imslp.org/wiki/Clarinet_Concerto_No.2,_Op.74_(Weber,_Carl_Maria_von)",
    "207-1-29681": "https://imslp.org/wiki/Clarinet_Concerto_in_A_major,_K.622_(Mozart,_Wolfgang_Amadeus)",
}


@dataclass
class ClarinetSoloRow:
    code: str
    event_name: str
    title: str
    composer: str
    arranger: str
    publisher_text: str
    grade: int
    specification: str


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def detect_school_year(homepage_html: str) -> str:
    match = YEAR_PATTERN.search(homepage_html)
    if not match:
        return DEFAULT_SCHOOL_YEAR
    return match.group(1)


def clarinet_row_to_dict(row: ClarinetSoloRow) -> dict:
    publishers = normalize_publishers(row.publisher_text)
    specification = clean_text(row.specification)
    return {
        "uilCode": row.code,
        "eventName": row.event_name,
        "title": clean_text(row.title),
        "composer": clean_text(row.composer),
        "arranger": clean_text(row.arranger),
        "publishers": publishers,
        "publisherText": ";".join(publishers),
        "classLevel": row.grade,
        "specification": specification,
        "noMemoryRequired": "NMR:" in specification,
    }


def fetch_clarinet_rows() -> list[ClarinetSoloRow]:
    payload = fetch_json(UIL_DATA)
    rows = []
    for entry in payload["pml"]:
        if len(entry) < 8:
            continue
        event_name = entry[1].strip()
        if "Clarinet Solo" not in event_name:
            continue
        rows.append(
            ClarinetSoloRow(
                code=entry[0].strip(),
                event_name=event_name,
                title=entry[2].strip(),
                composer=entry[3].strip(),
                arranger=entry[4].strip(),
                publisher_text=entry[5].strip(),
                grade=int(entry[6].strip()),
                specification=entry[7].strip(),
            )
        )
    return rows


def write_source_csv(rows: list[ClarinetSoloRow], destination: Path) -> None:
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
            cleaned = clarinet_row_to_dict(row)
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


def load_cache() -> dict[str, dict]:
    if not PUBLIC_DOMAIN_CACHE_PATH.exists():
        return {}
    return json.loads(PUBLIC_DOMAIN_CACHE_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, dict]) -> None:
    PUBLIC_DOMAIN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_DOMAIN_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def song_key(song: ClarinetSoloRow) -> str:
    return f"{song.event_name}::{clean_text(song.composer)}::{clean_text(song.title)}"


def instrument_terms(event_name: str) -> list[str]:
    lowered = event_name.lower()
    if "contra bass" in lowered:
        return ["contra bass clarinet", "contrabass clarinet", "clarinet"]
    if "bass clarinet" in lowered:
        return ["bass clarinet", "clarinet"]
    if "alto clarinet" in lowered:
        return ["alto clarinet", "clarinet"]
    if "eb clarinet" in lowered:
        return ["eb clarinet", "e flat clarinet", "e-flat clarinet", "clarinet"]
    return ["clarinet"]


def parse_ddg_result_url(raw_url: str) -> str:
    decoded = html.unescape(raw_url)
    if "uddg=" not in decoded:
        return decoded
    return urllib.parse.parse_qs(urllib.parse.urlparse(decoded).query).get("uddg", [""])[0]


def find_imslp_pages(query: str) -> list[str]:
    url = DDG_SEARCH_URL + urllib.parse.quote(query)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", "ignore")

    pages: list[str] = []
    for raw_url in DDG_RESULT_PATTERN.findall(body):
        candidate = parse_ddg_result_url(raw_url)
        if not candidate.startswith("https://imslp.org/wiki/"):
            continue
        if any(segment in candidate for segment in ("/wiki/File:", "/wiki/Category:", "/wiki/Talk:", "/wiki/Template:")):
            continue
        if candidate not in pages:
            pages.append(candidate)
    return pages[:4]


def clean_html_text(value: str) -> str:
    return " ".join(html.unescape(TAG_PATTERN.sub(" ", value or "")).split())


def is_public_domain_group(page_html: str, file_id: str) -> bool:
    for match in IMSLP_INDEX_GROUP_PATTERN.finditer(page_html):
        ids = match.group(1).split("/")
        if file_id not in ids:
            continue
        snippet = page_html[max(0, match.start() - 1000) : match.start() + 1200]
        return "Public Domain" in snippet and "Non-PD US" not in snippet
    return False


def build_direct_pdf_url(relative_pdf_path: str, file_id: str) -> str:
    relative = relative_pdf_path[len("/images/") :]
    folder, filename = relative.rsplit("/", 1)
    return f"https://s9.imslp.org/files/imglnks/usimg/{folder}/IMSLP{file_id}-{filename}"


def choose_pdf_from_imslp_page(page_url: str, event_name: str) -> dict | None:
    request = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        page_html = response.read().decode("utf-8", "ignore")

    terms = instrument_terms(event_name)
    fallback: dict | None = None

    for file_id, block_html in IMSLP_BLOCK_PATTERN.findall(page_html):
        pdf_match = IMSLP_PDF_PATTERN.search(block_html)
        if not pdf_match:
            continue

        title_match = IMSLP_TITLE_PATTERN.search(block_html)
        block_title = clean_html_text(title_match.group(1) if title_match else "")
        block_text = clean_html_text(block_html).lower()
        pdf_url = build_direct_pdf_url(pdf_match.group(1), file_id)

        if not is_public_domain_group(page_html, file_id):
            continue

        candidate = {
            "pdfUrl": pdf_url,
            "source": "IMSLP",
            "sourcePageUrl": page_url,
            "fileLabel": block_title,
        }

        if any(term in block_text for term in terms):
            return candidate
        if fallback is None and "clarinet" in block_text:
            fallback = candidate

    return fallback


def title_variants(title: str) -> list[str]:
    variants = [clean_text(title)]
    stripped_parenthetical = clean_text(re.sub(r"\s*\([^)]*\)", "", title))
    if stripped_parenthetical and stripped_parenthetical not in variants:
        variants.append(stripped_parenthetical)
    stripped_after_comma = clean_text(title.split(",")[0])
    if stripped_after_comma and stripped_after_comma not in variants:
        variants.append(stripped_after_comma)
    return variants


def find_public_domain_link(song: ClarinetSoloRow) -> dict | None:
    page_url = KNOWN_IMSLP_PAGES.get(song.code)
    if not page_url:
        return None
    try:
        return choose_pdf_from_imslp_page(page_url, song.event_name)
    except Exception:
        return None


def enrich_public_domain_links(rows: list[ClarinetSoloRow]) -> dict[str, dict]:
    cache = load_cache()
    links_by_code: dict[str, dict] = {}

    for index, song in enumerate(rows, start=1):
        key = song_key(song)
        cached = cache.get(key)
        if cached and cached.get("pdfUrl"):
            links_by_code[song.code] = cached
            continue

        link = find_public_domain_link(song)
        if link:
            cache[key] = link
            links_by_code[song.code] = link
            save_cache(cache)
            print(f"[{index}/{len(rows)}] linked {song.event_name} | {song.composer} | {song.title}")
        elif index % 50 == 0:
            print(f"[{index}/{len(rows)}] checked through {song.event_name} | {song.composer} | {song.title}")

    save_cache(cache)
    return links_by_code


def build_outputs(
    rows: list[ClarinetSoloRow],
    *,
    school_year: str,
    source_label: str,
    source_csv_path: Path | None = None,
    public_domain_links: dict[str, dict] | None = None,
) -> dict:
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    songs_payload = []
    for index, row in enumerate(rows, start=1):
        payload = clarinet_row_to_dict(row)
        link_info = (public_domain_links or {}).get(row.code, {})
        payload["publicDomainPdfUrl"] = link_info.get("pdfUrl")
        payload["publicDomainSource"] = link_info.get("source")
        payload["publicDomainSourcePageUrl"] = link_info.get("sourcePageUrl")
        payload["publicDomainFileLabel"] = link_info.get("fileLabel")
        payload["id"] = index
        songs_payload.append(payload)

    songs_payload.sort(
        key=lambda song: (
            -song["classLevel"],
            song["eventName"],
            song["composer"],
            song["title"],
        )
    )

    stats_payload = {
        "schoolYear": school_year,
        "songCount": len(songs_payload),
        "publisherCount": sum(len(song["publishers"]) for song in songs_payload),
        "noteCount": 2,
        "databaseRecordCount": len(songs_payload) + 2,
        "classBreakdown": {
            "3": sum(song["classLevel"] == 3 for song in songs_payload),
            "2": sum(song["classLevel"] == 2 for song in songs_payload),
            "1": sum(song["classLevel"] == 1 for song in songs_payload),
        },
        "noMemoryRequiredCount": sum(song["noMemoryRequired"] for song in songs_payload),
        "publicDomainPdfCount": sum(bool(song["publicDomainPdfUrl"]) for song in songs_payload),
        "eventBreakdown": {
            event_name: sum(song["eventName"] == event_name for song in songs_payload)
            for event_name in sorted({song["eventName"] for song in songs_payload})
        },
        "notes": {
            "source_song_count": str(len(rows)),
            "dataset_audit": (
                f"Sourced from {source_label}. "
                f"Imported {datetime.now(timezone.utc).isoformat()}."
            ),
        },
    }

    CLARINET_SONGS_PATH.write_text(json.dumps(songs_payload, indent=2), encoding="utf-8")
    CLARINET_STATS_PATH.write_text(json.dumps(stats_payload, indent=2), encoding="utf-8")

    if source_csv_path is not None:
        write_source_csv(rows, source_csv_path)

    return stats_payload


def main() -> int:
    homepage_html = fetch_text(UIL_HOME)
    school_year = detect_school_year(homepage_html)
    clarinet_rows = fetch_clarinet_rows()
    public_domain_links = enrich_public_domain_links(clarinet_rows)
    stats = build_outputs(
        clarinet_rows,
        school_year=school_year,
        source_label=f"{UIL_HOME} and {UIL_DATA}",
        source_csv_path=SOURCE_CSV_PATH,
        public_domain_links=public_domain_links,
    )
    print(
        json.dumps(
            {
                "schoolYear": school_year,
                "songCount": stats["songCount"],
                "noMemoryRequiredCount": stats["noMemoryRequiredCount"],
                "publicDomainPdfCount": stats["publicDomainPdfCount"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
