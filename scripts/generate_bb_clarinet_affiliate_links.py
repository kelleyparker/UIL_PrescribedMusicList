from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV_PATH = ROOT / "data" / "uil_bb_clarinet_solos_source.csv"
OUTPUT_PATH = ROOT / "data" / "bb_clarinet_affiliate_links.json"

STOP_TOKENS = {"the", "a", "an", "from", "and", "in", "for", "of", "no", "op", "mvt"}
GENERIC_PUBLISHER_TOKENS = {
    "music",
    "company",
    "inc",
    "publications",
    "press",
    "edition",
    "publishers",
    "publisher",
    "co",
}
NON_SOLO_HINTS = {
    "quartet",
    "trio",
    "choir",
    "ensemble",
    "band",
    "orchestra",
    "duet",
    "octet",
}
SPECIAL_COMPOSER_KEYS = {
    "anon. or trad.": {"anon", "trad", "traditional"},
    "english folk song": {"english", "folk"},
}


@dataclass(frozen=True)
class SoloRow:
    code: str
    title: str
    composer: str
    arranger: str
    publisher: str


def normalize_text(value: str) -> str:
    lowered = (value or "").lower().replace("&", " and ")
    lowered = (
        lowered.replace("e-flat", "eb")
        .replace("b-flat", "bb")
        .replace("e flat", "eb")
        .replace("b flat", "bb")
    )
    lowered = re.sub(r"['’]", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def tokenize(value: str) -> list[str]:
    return [
        token
        for token in normalize_text(value).split()
        if token not in STOP_TOKENS and len(token) > 1
    ]


def title_variants(title: str) -> list[str]:
    variants: list[str] = []

    def add(value: str) -> None:
        cleaned = value.strip()
        if cleaned and cleaned not in variants:
            variants.append(cleaned)

    add(title)
    add(re.sub(r"\s*\([^)]*\)", "", title))
    add(title.split(",")[0])
    add(title.replace("'", ""))
    add(title.replace("-", " "))
    add(title.replace(":", " "))
    if " - " in title:
        add(title.split(" - ")[0])

    return variants


def composer_keys(composer: str) -> set[str]:
    normalized = normalize_text(composer)
    if normalized in SPECIAL_COMPOSER_KEYS:
        return set(SPECIAL_COMPOSER_KEYS[normalized])

    keys = {normalized}
    parts = [part for part in normalized.split() if part]
    if parts:
        keys.add(parts[-1])
    if "," in composer:
        keys.add(normalize_text(composer.split(",")[0]))
    if " or " in normalized:
        keys.update(part.strip() for part in normalized.split(" or "))
    return {key for key in keys if key}


def read_rows() -> list[SoloRow]:
    with SOURCE_CSV_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            SoloRow(
                code=row["Code"].strip(),
                title=row["Title"].strip(),
                composer=row["Composer"].strip(),
                arranger=row["Arranger"].strip(),
                publisher=row["Publisher [Collection]"].strip(),
            )
            for row in reader
        ]


def fetch_products(query: str, cache: dict[str, list[dict]]) -> list[dict]:
    if query in cache:
        return cache[query]

    url = (
        "https://www.jwpepper.com/api/catalog_system/pub/products/search"
        f"?ft={urllib.parse.quote(query)}&_from=0&_to=5"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except Exception:
        payload = []

    cache[query] = payload
    time.sleep(0.04)
    return payload


def product_instruments(product: dict) -> list[str]:
    instruments: list[str] = []
    for item in product.get("items", []):
        values = item.get("Instrument") or []
        if isinstance(values, list):
            instruments.extend(normalize_text(value) for value in values)
    return instruments


def product_title_text(product: dict) -> str:
    parts = [product.get("productName", ""), product.get("productTitle", "")]
    for key in ("Index Title", "Subtitle"):
        values = product.get(key) or []
        if isinstance(values, list):
            parts.extend(values)
    return " | ".join(parts)


def product_composer_text(product: dict) -> str:
    parts: list[str] = []
    for key in ("Composer", "Index Composer"):
        values = product.get(key) or []
        if isinstance(values, list):
            parts.extend(values)
    return " | ".join(parts)


def score_candidate(row: SoloRow, product: dict) -> int:
    normalized_title_text = normalize_text(product_title_text(product))
    normalized_composer_text = normalize_text(product_composer_text(product))
    normalized_description = normalize_text((product.get("description") or "")[:500])
    normalized_brand = normalize_text(product.get("brand", ""))
    instruments = product_instruments(product)
    joined_instruments = " ".join(instruments)

    score = 0
    has_clarinet = any("clarinet" in instrument for instrument in instruments)
    if has_clarinet:
        score += 35
    else:
        score -= 80

    if any(hint in joined_instruments for hint in NON_SOLO_HINTS):
        score -= 35

    if any(
        "keyboard accompaniment" in instrument or "piano accompaniment" in instrument
        for instrument in instruments
    ):
        score += 4

    for variant in title_variants(row.title):
        normalized_variant = normalize_text(variant)
        if not normalized_variant:
            continue
        if normalized_variant == normalized_title_text:
            score += 120
        elif normalized_variant in normalized_title_text:
            score += 60
        score += int(SequenceMatcher(None, normalized_variant, normalized_title_text).ratio() * 25)

        variant_tokens = tokenize(variant)
        overlap = sum(token in normalized_title_text for token in variant_tokens)
        if variant_tokens and overlap == len(variant_tokens):
            score += 35
        elif variant_tokens and overlap >= max(1, len(variant_tokens) - 1):
            score += 18

    row_composer_keys = composer_keys(row.composer)
    if any(key in normalized_composer_text for key in row_composer_keys):
        score += 45
    elif normalize_text(row.composer) not in SPECIAL_COMPOSER_KEYS:
        score -= 20

    arranger_tokens = [token for token in tokenize(row.arranger) if len(token) > 2]
    if arranger_tokens and any(
        token in normalized_composer_text or token in normalized_description
        for token in arranger_tokens
    ):
        score += 15

    publisher_tokens = [
        token
        for token in tokenize(row.publisher)
        if token not in GENERIC_PUBLISHER_TOKENS
    ]
    if publisher_tokens and any(
        token in normalized_brand or token in normalized_description
        for token in publisher_tokens
    ):
        score += 10

    return score


def find_best_match(row: SoloRow, cache: dict[str, list[dict]]) -> tuple[int | None, dict | None]:
    candidates: list[tuple[int, dict]] = []
    seen_links: set[str] = set()
    for query in title_variants(row.title)[:5]:
        for product in fetch_products(query, cache):
            link = product.get("link")
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            candidates.append((score_candidate(row, product), product))

    if not candidates:
        return None, None

    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    return candidates[0]


def build_links(rows: list[SoloRow], threshold: int) -> tuple[dict[str, dict], list[dict]]:
    cache: dict[str, list[dict]] = {}
    links: dict[str, dict] = {}
    review_rows: list[dict] = []

    for index, row in enumerate(rows, start=1):
        score, product = find_best_match(row, cache)
        if product is not None and score is not None and score >= threshold:
            links[row.code] = {
                "url": product["link"],
                "label": "Buy Sheet Music",
                "source": "JW Pepper link",
            }
        else:
            review_rows.append(
                {
                    "code": row.code,
                    "title": row.title,
                    "composer": row.composer,
                    "score": score,
                    "candidateName": product.get("productName") if product else None,
                    "candidateUrl": product.get("link") if product else None,
                }
            )

        if index % 25 == 0:
            print(
                f"[{index}/{len(rows)}] matched={len(links)} needs_review={len(review_rows)}",
                flush=True,
            )

    return links, review_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--threshold", type=int, default=95)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--review-output", type=Path, default=None)
    args = parser.parse_args()

    rows = read_rows()
    if args.limit > 0:
        rows = rows[: args.limit]

    links, review_rows = build_links(rows, threshold=args.threshold)
    args.output.write_text(json.dumps(links, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "rowsProcessed": len(rows),
                "matched": len(links),
                "needsReview": len(review_rows),
                "output": str(args.output),
            },
            indent=2,
        )
    )

    if args.review_output is not None:
        args.review_output.write_text(json.dumps(review_rows, indent=2), encoding="utf-8")
        print(f"review output written to {args.review_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
