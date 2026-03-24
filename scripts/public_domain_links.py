from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_piano_solos import PianoSoloRow, clean_text


ROOT = Path(__file__).resolve().parents[1]
LINKS_CACHE_PATH = ROOT / "data" / "public_domain_links.json"
IMSLP_SEARCH_URL = "https://imslp.org/api.php?action=query&list=search&format=json&srlimit=5&srsearch="
IMSLP_PAGE_URL = "https://imslp.org/wiki/"
FILE_PAIR_PATTERN = re.compile(
    r'Special:ImagefromIndex/(\d+).*?href="(/images/[^"]+\.pdf)"',
    re.DOTALL,
)
TOKEN_PATTERN = re.compile(r"[A-Za-z]{4,}")
TITLE_STOPWORDS = {
    "from",
    "major",
    "minor",
    "allegro",
    "andante",
    "adagio",
    "presto",
    "romance",
    "sonata",
    "sonatina",
    "concerto",
    "concertino",
    "rondo",
    "suite",
    "piece",
}


def song_key(song: PianoSoloRow) -> str:
    return f"{clean_text(song.composer)}::{clean_text(song.title)}"


def load_cache(cache_path: Path = LINKS_CACHE_PATH) -> dict[str, dict]:
    if not cache_path.exists():
        return {}
    return json.loads(cache_path.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, dict], cache_path: Path = LINKS_CACHE_PATH) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def check_pdf_url(url: str) -> bool:
    try:
        request = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status == 200 and response.headers.get_content_type() == "application/pdf"
    except Exception:
        return False


def query_imslp_titles(query: str) -> list[str]:
    url = IMSLP_SEARCH_URL + urllib.parse.quote(query)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.load(response)
    return [entry["title"] for entry in payload.get("query", {}).get("search", [])]


def page_title_to_url(title: str) -> str:
    return IMSLP_PAGE_URL + urllib.parse.quote(title.replace(" ", "_"), safe="(),._-")


def extract_pdf_candidates(page_title: str) -> list[str]:
    request = urllib.request.Request(
        page_title_to_url(page_title),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", "ignore")

    candidates = []
    for index_id, image_path in FILE_PAIR_PATTERN.findall(html):
        relative = image_path[len("/images/") :]
        folder, filename = relative.rsplit("/", 1)
        candidates.append(
            f"https://s9.imslp.org/files/imglnks/usimg/{folder}/IMSLP{index_id}-{filename}"
        )
    return candidates


def title_variants(title: str) -> list[str]:
    variants = [clean_text(title)]
    for match in re.findall(r"\(([^)]*)\)", title):
        inner = clean_text(match)
        if inner and inner not in variants:
            variants.append(inner)
    stripped_parenthetical = clean_text(re.sub(r"\s*\([^)]*\)", "", title))
    if stripped_parenthetical and stripped_parenthetical not in variants:
        variants.append(stripped_parenthetical)
    stripped_after_comma = clean_text(title.split(",")[0])
    if stripped_after_comma and stripped_after_comma not in variants:
        variants.append(stripped_after_comma)
    return variants


def instrument_hint(song: PianoSoloRow) -> str:
    event_name = clean_text(song.event_name).lower()
    if "french horn" in event_name:
        return "horn"
    if "piano" in event_name:
        return "piano"
    return ""


def title_tokens(title: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_PATTERN.findall(clean_text(title))
        if token.lower() not in TITLE_STOPWORDS
    ]


def page_title_matches(song: PianoSoloRow, page_title: str, variant: str) -> bool:
    normalized_page_title = clean_text(page_title).lower()
    composer = clean_text(song.composer).lower()
    composer_tokens = composer.split()
    if composer_tokens and composer_tokens[-1] not in normalized_page_title:
        return False

    hint = instrument_hint(song)
    if hint and hint not in normalized_page_title:
        return False

    tokens = title_tokens(variant)
    if not tokens:
        return True

    return any(token in normalized_page_title for token in tokens)


def find_public_domain_link(song: PianoSoloRow) -> dict | None:
    composer = clean_text(song.composer)
    hint = instrument_hint(song)
    for variant in title_variants(song.title)[:2]:
        query = " ".join(part for part in [composer, variant, hint] if part)
        try:
            for page_title in query_imslp_titles(query):
                if not page_title_matches(song, page_title, variant):
                    continue
                for url in extract_pdf_candidates(page_title)[:8]:
                    if check_pdf_url(url):
                        return {
                            "pdfUrl": url,
                            "source": "IMSLP",
                            "query": query,
                            "pageTitle": page_title,
                        }
        except Exception:
            continue
        time.sleep(0.15)
    return None


def enrich_public_domain_links(
    rows: list[PianoSoloRow],
    *,
    cache_path: Path = LINKS_CACHE_PATH,
) -> dict[str, dict]:
    cache = load_cache(cache_path)
    links_by_code: dict[str, dict] = {}

    for index, song in enumerate(rows, start=1):
        key = song_key(song)
        cached = cache.get(key)
        if cached and cached.get("pdfUrl") and check_pdf_url(cached["pdfUrl"]):
            links_by_code[song.code] = cached
            continue

        link = find_public_domain_link(song)
        if link:
            cache[key] = link
            links_by_code[song.code] = link
            save_cache(cache, cache_path)
            print(f"[{index}/{len(rows)}] linked {song.composer} - {song.title}")
        elif index % 25 == 0:
            print(f"[{index}/{len(rows)}] checked through {song.composer} - {song.title}")

    save_cache(cache, cache_path)
    return links_by_code
