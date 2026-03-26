from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

from import_piano_solos import (
    DEFAULT_SCHOOL_YEAR,
    INSTRUMENT_CONFIGS,
    SoloRow,
    affiliate_cache_path_for_instrument,
    build_from_csv,
    load_affiliate_links_cache,
    read_rows_from_csv,
)


JWPEPPER_SEARCH_URL = "https://www.jwpepper.com/api/catalog_system/pub/products/search/?ft="
TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "with",
    "movement",
    "mvt",
    "mvts",
    "play",
    "solo",
}
ENSEMBLE_KEYWORDS = {
    "solo": {"solo"},
    "trio": {"trio"},
    "quartet": {"quartet"},
    "quintet": {"quintet"},
    "choir": {"choir"},
    "chorus": {"chorus"},
    "ensemble": {"ensemble"},
    "orchestra": {"orchestra"},
    "band": {"band"},
}
PACE_PROFILES = {
    "safe": {
        "request_delay": (2.5, 5.0),
        "query_delay": (1.0, 2.0),
        "retry_base": 4.0,
        "max_retries": 4,
    },
    "normal": {
        "request_delay": (1.0, 2.5),
        "query_delay": (0.35, 0.9),
        "retry_base": 2.5,
        "max_retries": 3,
    },
    "fast": {
        "request_delay": (0.25, 0.75),
        "query_delay": (0.1, 0.25),
        "retry_base": 1.0,
        "max_retries": 2,
    },
}


def sleep_range(delay_range: tuple[float, float]) -> None:
    low, high = delay_range
    time.sleep(random.uniform(low, high))


def normalize(text: str) -> str:
    text = (text or "").lower().replace("&", " and ")
    text = re.sub(r"\bop\.?\s*", "op ", text)
    text = re.sub(r"\bk\.?\s*", "k ", text)
    text = re.sub(r"\brv\.?\s*", "rv ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def csv_row_to_dict(row: SoloRow) -> dict[str, str]:
    return {
        "Code": row.code,
        "Event Name": row.event_name,
        "Title": row.title,
        "Composer": row.composer,
        "Arranger": row.arranger,
        "Publisher [Collection]": row.publisher_text,
        "Grade": str(row.grade),
        "Specification": row.specification,
    }


def publisher_collection(publisher_text: str) -> str:
    match = re.search(r"\[(.*?)\]", publisher_text or "")
    return match.group(1).strip() if match else ""


def title_variants(row: dict[str, str]) -> list[str]:
    title = row["Title"]
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
    add(publisher_collection(row["Publisher [Collection]"]))
    return variants


def title_tokens(row: dict[str, str]) -> set[str]:
    return {
        token
        for variant in title_variants(row)
        for token in normalize(variant).split()
        if len(token) > 2 and token not in TITLE_STOPWORDS
    }


def query_variants(row: dict[str, str], instrument_slug: str) -> list[str]:
    instrument_hint = instrument_slug.replace("-", " ")
    queries = [
        f"{row['Title']} {row['Composer']} {instrument_hint}",
        f"{row['Title']} {instrument_hint}",
        f"{row['Title']} {row['Composer']}",
    ]

    if row["Arranger"]:
        queries.append(f"{row['Title']} {row['Arranger']} {instrument_hint}")
    if collection := publisher_collection(row["Publisher [Collection]"]):
        queries.append(f"{collection} {row['Composer']} {instrument_hint}")
        queries.append(f"{collection} {row['Composer']}")
    if row["Publisher [Collection]"]:
        queries.append(f"{row['Title']} {row['Publisher [Collection]']} {instrument_hint}")

    deduped: list[str] = []
    seen: set[str] = set()
    for query in queries:
        cleaned = " ".join(query.split())
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            deduped.append(cleaned)
    return deduped


def fetch_products(query: str, pace: dict[str, object]) -> list[dict]:
    url = JWPEPPER_SEARCH_URL + urllib.parse.quote(query)
    max_retries = int(pace["max_retries"])
    retry_base = float(pace["retry_base"])
    request_delay = pace["request_delay"]

    for attempt in range(max_retries):
        sleep_range(request_delay)
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "-A", "Mozilla/5.0", url],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout)
        except Exception:
            if attempt == max_retries - 1:
                raise
            backoff_seconds = retry_base * (2**attempt) + random.uniform(0.1, 0.8)
            time.sleep(backoff_seconds)
    return []


def product_search_text(product: dict) -> str:
    item_text = []
    for item in product.get("items") or []:
        item_text.extend(item.get("Instrument") or [])
        item_text.extend(item.get("Instrument Type") or [])
        item_text.extend(item.get("Ensemble") or [])
        item_text.extend(item.get("Format") or [])
        item_text.append(item.get("nameComplete", ""))
    return normalize(
        " ".join(
            [
                product.get("productName", ""),
                product.get("productTitle", ""),
                product.get("brand", ""),
                product.get("description", ""),
                " ".join(product.get("Composer") or []),
                " ".join(product.get("Index Composer") or []),
                " ".join(product.get("Accompaniment") or []),
                " ".join(item_text),
            ]
        )
    )


def composer_matches(song_composer: str, product: dict) -> bool:
    normalized_song = normalize(song_composer)
    if not normalized_song:
        return True

    composer_text = normalize(
        " ".join((product.get("Composer") or []) + (product.get("Index Composer") or []))
    )
    if not composer_text:
        return False

    song_tokens = [
        token
        for token in normalized_song.split()
        if token not in {"anon", "or", "trad", "traditional", "various"}
    ]
    if not song_tokens:
        return True
    product_tokens = set(composer_text.split())
    return (
        any(token in product_tokens for token in song_tokens)
        or normalized_song in composer_text
        or composer_text in normalized_song
    )


def event_keywords(event_name: str) -> set[str]:
    normalized = normalize(event_name)
    matched = set()
    for label, keywords in ENSEMBLE_KEYWORDS.items():
        if label in normalized:
            matched |= keywords
    return matched


def instrument_matches(product: dict, instrument_slug: str) -> bool:
    product_text = product_search_text(product)
    primary = normalize(instrument_slug.replace("-", " "))
    if primary and primary in product_text:
        return True

    aliases = {
        "bb clarinet": ["clarinet"],
        "eb clarinet": ["clarinet"],
        "bass clarinet": ["clarinet"],
        "alto clarinet": ["clarinet"],
        "contra bass clarinet": ["clarinet"],
        "french horn": ["horn"],
        "tenor trombone": ["trombone"],
        "bass trombone": ["trombone"],
        "alto saxophone": ["saxophone"],
        "tenor saxophone": ["saxophone"],
        "baritone saxophone": ["saxophone"],
        "soprano saxophone": ["saxophone"],
        "piccolo": ["piccolo", "flute piccolo"],
    }
    for alias in aliases.get(primary, []):
        if alias in product_text:
            return True
    return False


def score_product(row: dict[str, str], product: dict, instrument_slug: str) -> int:
    score = 0
    searchable = product_search_text(product)
    if not searchable:
        return -999

    product_name = normalize(product.get("productName", ""))
    product_title = normalize(product.get("productTitle", ""))
    normalized_variants = [normalize(variant) for variant in title_variants(row) if normalize(variant)]

    if any(variant == product_name or variant == product_title for variant in normalized_variants):
        score += 100
    if any(variant and variant in searchable for variant in normalized_variants):
        score += 30

    tokens = title_tokens(row)
    searchable_tokens = set(searchable.split())
    token_matches = sum(token in searchable_tokens for token in tokens)
    score += token_matches * 6
    score -= max(0, len(tokens) - token_matches) * 2

    if composer_matches(row["Composer"], product):
        score += 45
    elif row["Composer"]:
        score -= 50

    if instrument_matches(product, instrument_slug):
        score += 30
    else:
        score -= 20

    keywords = event_keywords(row["Event Name"])
    if keywords:
        keyword_hits = sum(keyword in searchable for keyword in keywords)
        score += keyword_hits * 15
        if "solo" in keywords and "solo" not in searchable:
            score -= 25

    publisher_text = normalize(row["Publisher [Collection]"])
    brand = normalize(product.get("brand", ""))
    if brand and publisher_text:
        if brand in publisher_text or publisher_text in brand:
            score += 18
        elif any(token in brand for token in publisher_text.split()[:3]):
            score += 6

    if "collection" in searchable and publisher_collection(row["Publisher [Collection]"]):
        score += 5
    if "with piano" in searchable:
        score += 2

    return score


def choose_best_product(
    row: dict[str, str], instrument_slug: str, pace: dict[str, object]
) -> tuple[dict | None, int]:
    best_match: tuple[int, dict] | None = None
    for query in query_variants(row, instrument_slug):
        try:
            products = fetch_products(query, pace)
        except Exception:
            sleep_range(pace["query_delay"])
            continue
        for product in products:
            candidate_score = score_product(row, product, instrument_slug)
            if best_match is None or candidate_score > best_match[0]:
                best_match = (candidate_score, product)
        if best_match and best_match[0] >= 120:
            break
        sleep_range(pace["query_delay"])
    if not best_match:
        return None, 0
    return best_match[1], best_match[0]


def parse_args() -> argparse.Namespace:
    instrument_list = "\n".join(f"  - {slug}" for slug in sorted(INSTRUMENT_CONFIGS))
    parser = argparse.ArgumentParser(
        description="Build affiliate link caches for a UIL PML instrument."
        "\n\nThis writes an instrument-specific affiliate cache in data/ and then"
        "\nrebuilds that instrument's static JSON in static/data/.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/build_affiliate_links.py --instrument piccolo --class-level 3\n"
            "  python3 scripts/build_affiliate_links.py --instrument steel-band --all-classes --pace safe\n"
            "  python3 scripts/build_affiliate_links.py --instrument flute --class-level 1 --class-level 2 --dry-run\n"
            "\n"
            "Available instrument slugs:\n"
            f"{instrument_list}"
        ),
    )
    parser.add_argument(
        "--instrument",
        required=True,
        choices=sorted(INSTRUMENT_CONFIGS),
        metavar="SLUG",
        help="Instrument/category slug to update.",
    )
    class_group = parser.add_mutually_exclusive_group()
    class_group.add_argument(
        "--class-level",
        type=int,
        action="append",
        dest="class_levels",
        metavar="N",
        help=(
            "Limit the run to one or more UIL class levels.\n"
            "Repeat this flag to include multiple classes."
        ),
    )
    class_group.add_argument(
        "--all-classes",
        action="store_true",
        help="Process every class level for the selected instrument.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-check rows even if they already exist in the affiliate cache.",
    )
    parser.add_argument(
        "--pace",
        choices=sorted(PACE_PROFILES),
        default="normal",
        help=(
            "Request pacing profile.\n"
            "safe = slowest / least bot-like, normal = balanced, fast = quickest."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Only process the first N matching rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview matches without writing cache files or rebuilding JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = INSTRUMENT_CONFIGS[args.instrument]
    csv_path = config["csv_path"]
    cache_path = affiliate_cache_path_for_instrument(args.instrument)
    existing_cache = load_affiliate_links_cache(cache_path)
    pace = PACE_PROFILES[args.pace]

    rows = read_rows_from_csv(csv_path)
    if args.class_levels:
        allowed_levels = set(args.class_levels)
        rows = [row for row in rows if row.grade in allowed_levels]
    if args.limit:
        rows = rows[: args.limit]

    updated_cache = dict(existing_cache)
    matches: list[dict[str, object]] = []

    for index, row in enumerate(rows, start=1):
        if not args.force and row.code in updated_cache:
            continue

        result_row = csv_row_to_dict(row)
        product, score = choose_best_product(result_row, args.instrument, pace)
        if product and score >= 85:
            updated_cache[row.code] = {
                "url": product["link"],
                "label": "Buy Sheet Music",
                "source": "JW Pepper link",
            }
            matches.append(
                {
                    "code": row.code,
                    "title": row.title,
                    "score": score,
                    "url": product["link"],
                    "productName": product.get("productName"),
                }
            )
            print(
                f"[{index}/{len(rows)}] matched {row.code} {row.title} -> {product['link']} (score={score})",
                flush=True,
            )
        else:
            print(
                f"[{index}/{len(rows)}] no confident match for {row.code} {row.title} (score={score})",
                flush=True,
            )

    if args.dry_run:
        print(json.dumps(matches, indent=2))
        return 0

    cache_path.write_text(
        json.dumps(dict(sorted(updated_cache.items())), indent=2),
        encoding="utf-8",
    )

    build_from_csv(
        csv_path,
        school_year=DEFAULT_SCHOOL_YEAR,
        source_label="local CSV snapshots",
        instrument_slug=args.instrument,
        affiliate_links=updated_cache,
    )

    print(
        json.dumps(
            {
                "instrument": args.instrument,
                "pace": args.pace,
                "cachePath": str(cache_path),
                "rowsConsidered": len(rows),
                "matchedThisRun": len(matches),
                "totalCachedLinks": len(updated_cache),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
