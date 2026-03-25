from __future__ import annotations

import csv
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

from import_piano_solos import (  # noqa: E402
    FRENCH_HORN_AFFILIATE_LINKS_PATH,
    FRENCH_HORN_SOURCE_CSV_PATH,
    build_from_csv,
)


JWPEPPER_SEARCH_URL = "https://www.jwpepper.com/api/catalog_system/pub/products/search/?ft="
TITLE_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "horn",
    "solo",
    "piano",
    "movement",
    "mvt",
    "mvts",
    "play",
}
MANUAL_OVERRIDES = {
    "302-3-12839": {
        "url": "https://www.jwpepper.com/canzona-996926/p",
        "label": "Buy Sheet Music",
        "source": "JW Pepper link",
    },
    "302-3-12841": {
        "url": "https://www.jwpepper.com/may-song-french-horn-solo-5006424/p",
        "label": "Buy Sheet Music",
        "source": "JW Pepper link",
    },
}
PUBLIC_DOMAIN_OVERRIDES = {
    "302-2-37349": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/7/79/IMSLP472912-PMLP228488-The_Alpine_Horn.pdf",
        "source": "IMSLP",
    },
    "302-2-12827": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/0/05/IMSLP345813-PMLP412673-Scriabin_-_Romance.pdf",
        "source": "IMSLP",
    },
    "302-1-32399": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/1/14/IMSLP919227-PMLP1444213-Basler_Four_Hymn_Tune_Settings_for_horn_and_piano.pdf",
        "source": "IMSLP",
    },
    "302-1-12746": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/8/82/IMSLP13557-Mozart-Horn_Quintet_K.407.pdf",
        "source": "IMSLP",
    },
    "302-1-12750": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/2/27/IMSLP01492-Mozart_-_Horn_Concerto_No.2.pdf",
        "source": "IMSLP",
    },
    "302-1-12751": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/e/e2/IMSLP01493-Mozart_-_Horn_Concerto_No.3.pdf",
        "source": "IMSLP",
    },
    "302-1-12755": {
        "pdfUrl": "https://s9.imslp.org/files/imglnks/usimg/b/b9/IMSLP365428-PMLP04595-WAMozart_Horn_Concerto%2C_K.495_WAMWS12B2N19_1886rev.pdf",
        "source": "IMSLP",
    },
}


def normalize(text: str) -> str:
    text = (text or "").lower().replace("&", " and ")
    text = re.sub(r"\bop\.?\s*", "op ", text)
    text = re.sub(r"\bk\.?\s*", "k ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def title_variants(title: str, publisher: str) -> list[str]:
    variants: list[str] = []

    def add(value: str) -> None:
        value = (value or "").strip()
        if value and value not in variants:
            variants.append(value)

    add(title)
    add(re.sub(r"\s*\([^)]*\)", "", title).strip())
    if ":" in title:
        left, right = title.split(":", 1)
        add(left)
        add(right)
    if "," in title:
        add(title.split(",", 1)[0])
    for match in re.findall(r"\(([^)]*)\)", title):
        add(match)
    publisher_collection = re.search(r"\[(.*?)\]", publisher or "")
    if publisher_collection:
        add(publisher_collection.group(1))
    return variants


def title_tokens(title: str, publisher: str) -> set[str]:
    return {
        token
        for variant in title_variants(title, publisher)
        for token in normalize(variant).split()
        if len(token) > 2 and token not in TITLE_STOPWORDS
    }


def composer_matches(song_composer: str, product: dict) -> bool:
    normalized_song = normalize(song_composer)
    if not normalized_song:
        return True

    normalized_product = normalize(
        " ".join((product.get("Composer") or []) + (product.get("Index Composer") or []))
    )
    if not normalized_product:
        return False

    song_tokens = [
        token
        for token in normalized_song.split()
        if token not in {"anon", "or", "trad", "traditional"}
    ]
    if not song_tokens:
        return True
    product_tokens = set(normalized_product.split())
    return (
        any(token in product_tokens for token in song_tokens)
        or normalized_song in normalized_product
        or normalized_product in normalized_song
    )


def horn_solo_matches(product: dict) -> bool:
    for item in product.get("items") or []:
        instrument_text = normalize(
            " ".join(
                (item.get("Instrument") or [])
                + (item.get("Instrument Type") or [])
                + [item.get("nameComplete", "")]
            )
        )
        ensemble_text = normalize(" ".join(item.get("Ensemble") or []))
        if "horn" in instrument_text and ("solo" in instrument_text or "solo" in ensemble_text):
            return True

    fallback_text = normalize(
        " ".join(
            [
                product.get("productName", ""),
                product.get("productTitle", ""),
                product.get("description", ""),
                " ".join(product.get("Accompaniment") or []),
            ]
        )
    )
    return "horn" in fallback_text and "solo" in fallback_text


def score_product(row: dict[str, str], product: dict) -> int:
    if not horn_solo_matches(product):
        return -999
    if row["Composer"] and not composer_matches(row["Composer"], product):
        return -999

    product_name = normalize(product.get("productName", ""))
    product_title = normalize(product.get("productTitle", ""))
    searchable = " ".join(
        [
            product_name,
            product_title,
            normalize(product.get("description", "")),
            normalize(" ".join(product.get("Accompaniment") or [])),
        ]
    ).strip()

    score = 0
    normalized_variants = [
        normalize(variant)
        for variant in title_variants(row["Title"], row["Publisher [Collection]"])
        if normalize(variant)
    ]
    exact_titles = {
        product_name,
        product_title,
        product_name.replace(" french horn solo", ""),
        product_title.replace(" sheet music", ""),
    }
    if any(variant in exact_titles for variant in normalized_variants):
        score += 100
    if any(variant and variant in searchable for variant in normalized_variants):
        score += 40

    tokens = title_tokens(row["Title"], row["Publisher [Collection]"])
    token_matches = sum(token in searchable.split() for token in tokens)
    score += token_matches * 5
    score -= max(0, len(tokens) - token_matches) * 2

    if row["Composer"]:
        score += 40

    brand = normalize(product.get("brand", ""))
    publisher = normalize(row["Publisher [Collection]"])
    if brand and publisher and any(token in brand for token in publisher.split()[:3]):
        score += 5

    if "with piano" in normalize(" ".join(product.get("Accompaniment") or [])):
        score += 3

    return score


def fetch_products(query: str) -> list[dict]:
    request = urllib.request.Request(
        JWPEPPER_SEARCH_URL + urllib.parse.quote(query),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def query_variants(row: dict[str, str]) -> list[str]:
    base_queries = [
        f"{row['Title']} {row['Composer']} French Horn",
        f"{row['Title']} French Horn",
    ]
    if row["Arranger"]:
        base_queries.append(f"{row['Title']} {row['Arranger']} French Horn")
    collection = re.search(r"\[(.*?)\]", row["Publisher [Collection]"] or "")
    if collection:
        base_queries.append(f"{collection.group(1)} {row['Composer']} French Horn")
    if not row["Composer"]:
        base_queries.append(f"{row['Title']} Horn and Piano")

    deduped: list[str] = []
    seen: set[str] = set()
    for query in base_queries:
        cleaned = " ".join(query.split())
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            deduped.append(cleaned)
    return deduped


def choose_best_product(row: dict[str, str]) -> dict | None:
    best_match: tuple[int, dict] | None = None
    for query in query_variants(row):
        try:
            products = fetch_products(query)
        except Exception:
            time.sleep(0.2)
            continue
        for product in products:
            candidate_score = score_product(row, product)
            if best_match is None or candidate_score > best_match[0]:
                best_match = (candidate_score, product)
        if best_match and best_match[0] >= 90:
            break
        time.sleep(0.1)
    if not best_match or best_match[0] < 90:
        return None
    return best_match[1]


def load_existing_cache() -> dict[str, dict]:
    if not FRENCH_HORN_AFFILIATE_LINKS_PATH.exists():
        return {}
    return json.loads(FRENCH_HORN_AFFILIATE_LINKS_PATH.read_text(encoding="utf-8"))


def build_affiliate_cache() -> dict[str, dict]:
    rows = list(csv.DictReader(FRENCH_HORN_SOURCE_CSV_PATH.open(encoding="utf-8-sig")))
    cache = load_existing_cache()
    cache.update(MANUAL_OVERRIDES)

    for index, row in enumerate(rows, start=1):
        if row["Code"] in cache:
            continue
        product = choose_best_product(row)
        if not product:
            if index % 10 == 0:
                print(f"[{index}/{len(rows)}] checked through {row['Title']}", flush=True)
            continue
        cache[row["Code"]] = {
            "url": product["link"],
            "label": "Buy Sheet Music",
            "source": "JW Pepper link",
        }
        if index % 10 == 0:
            print(f"[{index}/{len(rows)}] matched through {row['Title']}", flush=True)
            FRENCH_HORN_AFFILIATE_LINKS_PATH.write_text(
                json.dumps(dict(sorted(cache.items())), indent=2),
                encoding="utf-8",
            )

    FRENCH_HORN_AFFILIATE_LINKS_PATH.write_text(
        json.dumps(dict(sorted(cache.items())), indent=2),
        encoding="utf-8",
    )
    return cache


def main() -> int:
    affiliate_links = build_affiliate_cache()
    public_domain_links = PUBLIC_DOMAIN_OVERRIDES
    build_from_csv(
        FRENCH_HORN_SOURCE_CSV_PATH,
        source_label="local CSV snapshots",
        instrument_slug="french-horn",
        public_domain_links=public_domain_links,
        affiliate_links=affiliate_links,
    )
    print(
        json.dumps(
            {
                "affiliateLinkCount": len(affiliate_links),
                "publicDomainLinkCount": len(public_domain_links),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
