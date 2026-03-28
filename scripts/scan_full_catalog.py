#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from pml_catalog_core import (
    DEFAULT_SCHOOL_YEAR,
    INSTRUMENT_CONFIGS,
    affiliate_cache_path_for_instrument,
    build_from_csv,
    load_affiliate_links_cache,
    read_rows_from_csv,
)


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_PATH = LOG_DIR / "fill_sheet_music_links.log"

JWPEPPER_SEARCH_URL = "https://www.jwpepper.com/api/catalog_system/pub/products/search/?ft="
JWPEPPER_WEB_SEARCH_URL = "https://www.jwpepper.com/sheet-music/search.jsp?keywords={query}"
AMAZON_SEARCH_URL = "https://www.amazon.com/s?k={query}"
SMP_SEARCH_URL = "https://www.sheetmusicplus.com/search?Ntt={query}"
MUSICNOTES_SEARCH_URL = "https://www.musicnotes.com/search/go?w={query}"

GLOBAL_CONCURRENCY = 10
JWPEPPER_CONCURRENCY = 4
FALLBACK_CONCURRENCY = 2
AMAZON_RATE_LIMIT_TRIGGER = 3
AMAZON_RATE_LIMIT_COOLDOWN_SECONDS = 15 * 60
JWPEPPER_ONLY_MODE = True
ONLY_TEST_CODE = (os.getenv("ONLY_TEST_CODE") or "").strip() or None

# Rescan control:
# - none (default): process only codes missing in both cache and attempts files.
# - all: process all rows but keep existing cache/attempt history.
# - reset: clear cache + attempts in memory, then process all rows from scratch.
RESCAN_MODE = (os.getenv("SCAN_RESCAN_MODE") or "none").strip().lower()

# Throughput tuning (override with environment variables).
GLOBAL_CONCURRENCY = int(os.getenv("SCAN_GLOBAL_CONCURRENCY", "60"))
JWPEPPER_CONCURRENCY = int(os.getenv("SCAN_JWPEPPER_CONCURRENCY", "24"))
FALLBACK_CONCURRENCY = int(os.getenv("SCAN_FALLBACK_CONCURRENCY", "6"))

# Lower jitter on JW Pepper requests improves throughput substantially.
JWPEPPER_DELAY_MIN = float(os.getenv("SCAN_JWPEPPER_DELAY_MIN", "0.05"))
JWPEPPER_DELAY_MAX = float(os.getenv("SCAN_JWPEPPER_DELAY_MAX", "0.20"))
FALLBACK_DELAY_MIN = float(os.getenv("SCAN_FALLBACK_DELAY_MIN", "0.30"))
FALLBACK_DELAY_MAX = float(os.getenv("SCAN_FALLBACK_DELAY_MAX", "0.90"))

# Persist progress in batches to avoid rewriting large JSON files per row.
STATE_FLUSH_EVERY_ROWS = int(os.getenv("SCAN_STATE_FLUSH_EVERY_ROWS", "30"))
STATE_FLUSH_EVERY_SECONDS = float(os.getenv("SCAN_STATE_FLUSH_EVERY_SECONDS", "15"))

TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "edition",
    "for",
    "from",
    "in",
    "of",
    "on",
    "play",
    "solo",
    "suite",
    "the",
    "with",
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


@dataclass
class Candidate:
    url: str
    label: str
    source: str
    title: str
    metadata: dict[str, Any]


@dataclass
class DomainRateLimitState:
    consecutive_hits: int = 0
    disabled_until_epoch: float = 0.0
    last_cooldown_log_epoch: float = 0.0


AMAZON_RATE_LIMIT_STATE = DomainRateLimitState()


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def now_epoch() -> float:
    return datetime.now(timezone.utc).timestamp()


def amazon_is_temporarily_disabled() -> bool:
    return AMAZON_RATE_LIMIT_STATE.disabled_until_epoch > now_epoch()


def mark_amazon_rate_limited(reason: str) -> None:
    if amazon_is_temporarily_disabled():
        return

    AMAZON_RATE_LIMIT_STATE.consecutive_hits += 1
    logging.warning(
        "Amazon rate-limit signal (%s). consecutive_hits=%s/%s",
        reason,
        AMAZON_RATE_LIMIT_STATE.consecutive_hits,
        AMAZON_RATE_LIMIT_TRIGGER,
    )
    if AMAZON_RATE_LIMIT_STATE.consecutive_hits >= AMAZON_RATE_LIMIT_TRIGGER:
        AMAZON_RATE_LIMIT_STATE.disabled_until_epoch = now_epoch() + AMAZON_RATE_LIMIT_COOLDOWN_SECONDS
        AMAZON_RATE_LIMIT_STATE.consecutive_hits = 0
        logging.warning(
            "Amazon temporarily disabled for %s seconds due to rate limiting",
            AMAZON_RATE_LIMIT_COOLDOWN_SECONDS,
        )


def clear_amazon_rate_limit_signal() -> None:
    AMAZON_RATE_LIMIT_STATE.consecutive_hits = 0


def is_amazon_rate_limit_exception(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "returned error: 503",
        "returned error: 429",
        "service unavailable",
        "too many requests",
        "robot check",
        "captcha",
    )
    return any(marker in text for marker in markers)


def is_amazon_rate_limit_payload(payload: str) -> bool:
    lower_payload = (payload or "").lower()
    markers = (
        "enter the characters you see below",
        "type the characters you see in this image",
        "sorry, we just need to make sure you're not a robot",
        "to discuss automated access to amazon data",
    )
    return any(marker in lower_payload for marker in markers)


def attempt_cache_path_for_instrument(instrument_slug: str) -> Path:
    cache_path = affiliate_cache_path_for_instrument(instrument_slug)
    return cache_path.parent / f"{instrument_slug}_attempts.json"


def load_attempt_cache(cache_path: Path) -> dict[str, dict[str, Any]]:
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize(text: str) -> str:
    text = (text or "").lower().replace("&", " and ")
    # Keep possessive words as a single token (children's -> childrens)
    text = re.sub(r"([a-z0-9])'s\b", r"\1s", text)
    text = re.sub(r"\bopp\.?\s*", "op ", text)
    text = re.sub(r"\bop\.?\s*", "op ", text)
    text = re.sub(r"\bk\.?\s*", "k ", text)
    text = re.sub(r"\brv\.?\s*", "rv ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def publisher_collection(publisher_text: str) -> str:
    match = re.search(r"\[(.*?)\]", publisher_text or "")
    return match.group(1).strip() if match else ""


def title_variants(title: str, publisher_text: str) -> list[str]:
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
    add(publisher_collection(publisher_text))
    return variants


def title_tokens(title: str, publisher_text: str) -> set[str]:
    return {
        token
        for variant in title_variants(title, publisher_text)
        for token in normalize(variant).split()
        if len(token) > 2 and token not in TITLE_STOPWORDS
    }


def instrument_aliases(instrument_slug: str) -> list[str]:
    primary = instrument_slug.replace("-", " ")
    aliases = {
        "bb clarinet solo": ["clarinet"],
        "eb clarinet solo": ["clarinet"],
        "bass clarinet solo": ["clarinet"],
        "alto clarinet solo": ["clarinet"],
        "contra bass clarinet solo": ["clarinet"],
        "french horn": ["horn"],
        "tenor trombone": ["trombone"],
        "bass trombone": ["trombone"],
        "alto saxophone": ["saxophone"],
        "tenor saxophone": ["saxophone"],
        "baritone saxophone": ["saxophone"],
        "soprano saxophone": ["saxophone"],
        "string bass": ["bass"],
        "acoustical guitar": ["guitar"],
        "keyboard percussion": ["mallet", "marimba", "vibraphone", "xylophone"],
        "multiple percussion": ["percussion"],
        "drum set": ["drumset", "drums"],
        "steel pan": ["steelpan", "pan"],
    }
    return [primary, *aliases.get(primary, [])]


def query_variants(row: Any, instrument_slug: str) -> list[str]:
    instrument_hint = instrument_slug.replace("-", " ")
    title_and_variant = re.sub(r"\s+or\s+", " and ", row.title, flags=re.IGNORECASE)
    title_no_punct = re.sub(r"[,;:]", " ", row.title)
    queries = [
        f"{row.title} {row.composer} {instrument_hint}",
        f"{row.title} {instrument_hint}",
        f"{row.title} {row.composer}",
        f"{title_and_variant} {row.composer} {instrument_hint}",
        f"{title_and_variant} {row.composer}",
        f"{title_no_punct} {row.composer} {instrument_hint}",
    ]

    opus_numbers = re.findall(r"\bop\.?\s*(\d+)", row.title, flags=re.IGNORECASE)
    if opus_numbers:
        base_title = re.sub(r"\bop\.?\s*\d+", "", row.title, flags=re.IGNORECASE)
        base_title = re.sub(r"\s+(or|and)\s+", " ", base_title, flags=re.IGNORECASE)
        base_title = " ".join(base_title.split())
        for opus in dict.fromkeys(opus_numbers):
            queries.append(f"{base_title} op {opus} {row.composer} {instrument_hint}")
            queries.append(f"{base_title} op {opus} {row.composer}")

    if row.arranger:
        queries.append(f"{row.title} {row.arranger} {instrument_hint}")
    if collection := publisher_collection(row.publisher_text):
        queries.append(f"{collection} {row.composer} {instrument_hint}")
        queries.append(f"{collection} {row.composer}")
    if row.publisher_text:
        queries.append(f"{row.title} {row.publisher_text} {instrument_hint}")

    # Extra punctuation-safe variants improve matches on vendor endpoints.
    title_no_apostrophe = row.title.replace("'", "")
    queries.append(f"{title_no_apostrophe} {row.composer} {instrument_hint}")
    queries.append(f"{title_no_apostrophe} {row.composer}")
    queries.append(title_no_apostrophe)

    deduped: list[str] = []
    seen: set[str] = set()
    for query in queries:
        cleaned = " ".join(query.split())
        if cleaned and cleaned not in seen:
            deduped.append(cleaned)
            seen.add(cleaned)
    return deduped


def sanitize_jwpepper_query(query: str) -> str:
    # JW Pepper API can reject some punctuation-heavy queries with HTTP 400.
    cleaned = (query or "")
    cleaned = cleaned.replace("'", "")
    cleaned = cleaned.replace("\u2019", "")
    cleaned = re.sub(r"[^A-Za-z0-9\s,.-]", " ", cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned


def ensemble_keywords(event_name: str) -> set[str]:
    normalized = normalize(event_name)
    found = set()
    for label, keywords in ENSEMBLE_KEYWORDS.items():
        if label in normalized:
            found |= keywords
    return found


def composer_matches(song_composer: str, text: str) -> bool:
    normalized_song = normalize(song_composer)
    if not normalized_song:
        return True

    song_tokens = [
        token
        for token in normalized_song.split()
        if token not in {"anon", "or", "trad", "traditional", "various"}
    ]
    if not song_tokens:
        return True

    normalized_text = normalize(text)
    haystack = set(normalized_text.split())
    return any(token in haystack for token in song_tokens)


def candidate_text(candidate: Candidate) -> str:
    metadata = candidate.metadata or {}
    item_text = []
    for item in metadata.get("items") or []:
        item_text.extend(item.get("Instrument") or [])
        item_text.extend(item.get("Instrument Type") or [])
        item_text.extend(item.get("Ensemble") or [])
        item_text.extend(item.get("Format") or [])
        item_text.append(item.get("nameComplete", ""))

    return normalize(
        " ".join(
            [
                candidate.title,
                metadata.get("brand", ""),
                metadata.get("description", ""),
                " ".join(metadata.get("Composer") or []),
                " ".join(metadata.get("Index Composer") or []),
                " ".join(metadata.get("Accompaniment") or []),
                " ".join(item_text),
            ]
        )
    )


def score_candidate(row: Any, instrument_slug: str, candidate: Candidate) -> int:
    searchable = candidate_text(candidate)
    if not searchable:
        searchable = normalize(candidate.title)

    normalized_variants = [
        normalize(variant)
        for variant in title_variants(row.title, row.publisher_text)
        if normalize(variant)
    ]
    score = 0

    title_norm = normalize(candidate.title)
    if any(variant == title_norm for variant in normalized_variants):
        score += 120
    if any(variant and variant in searchable for variant in normalized_variants):
        score += 35

    tokens = title_tokens(row.title, row.publisher_text)
    searchable_tokens = set(searchable.split())
    token_matches = sum(token in searchable_tokens for token in tokens)
    score += token_matches * 6
    score -= max(0, len(tokens) - token_matches) * 2

    if composer_matches(row.composer, searchable):
        score += 40
    elif row.composer:
        score -= 20

    for alias in instrument_aliases(instrument_slug):
        if normalize(alias) in searchable:
            score += 25
            break
    else:
        if normalize(instrument_slug) not in {"piano", "piano solo"}:
            score -= 15

    keywords = ensemble_keywords(row.event_name)
    if keywords:
        hits = sum(keyword in searchable for keyword in keywords)
        score += hits * 12
        if "solo" in keywords and "solo" not in searchable and "collection" not in searchable:
            score -= 20

    brand = normalize(candidate.metadata.get("brand", ""))
    publisher = normalize(row.publisher_text)
    if brand and publisher:
        if brand in publisher or publisher in brand:
            score += 15
        elif any(token in brand for token in publisher.split()[:3]):
            score += 6

    if candidate.source == "JW Pepper link":
        score += 12
    elif candidate.source == "Amazon link":
        score += 4

    row_title_norm = normalize(row.title)
    candidate_title_norm = normalize(candidate.title)
    collection_tokens = {"anthology", "collection", "album", "library", "sampler", "works"}
    if any(token in candidate_title_norm.split() for token in collection_tokens):
        if not any(token in row_title_norm.split() for token in collection_tokens):
            score -= 80

    return score


async def run_curl(url: str) -> str:
    process = await asyncio.create_subprocess_exec(
        "curl",
        "-LfsS",
        "-A",
        "Mozilla/5.0",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(stderr.decode("utf-8", "ignore").strip() or f"curl failed: {url}")
    return stdout.decode("utf-8", "ignore")


async def fetch_with_retries(
    url: str,
    *,
    domain_semaphore: asyncio.Semaphore,
    retries: int = 3,
    min_delay: float = 0.5,
    max_delay: float = 1.5,
) -> str:
    for attempt in range(retries):
        try:
            async with domain_semaphore:
                await asyncio.sleep(random.uniform(min_delay, max_delay))
                return await run_curl(url)
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep((2**attempt) + random.uniform(0.2, 1.0))
    return ""


def extract_jwpepper_candidates(payload: str) -> list[Candidate]:
    try:
        products = json.loads(payload)
    except Exception:
        return []

    candidates: list[Candidate] = []
    for product in products[:10]:
        link = product.get("link")
        name = product.get("productName") or product.get("productTitle") or ""
        if not link or not name:
            continue
        candidates.append(
            Candidate(
                url=link,
                label="Buy Sheet Music",
                source="JW Pepper link",
                title=name,
                metadata=product,
            )
        )
    return candidates


def extract_jwpepper_web_candidates(payload: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    pattern = re.compile(
        r'<a[^>]+href="(?P<href>/[^"\s]+-\d+/p(?:\?[^"#]*)?)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    seen: set[str] = set()
    for match in pattern.finditer(payload):
        href = match.group("href")
        title = re.sub(r"<[^>]+>", " ", match.group("title"))
        title = " ".join(title.split())
        if not href or not title:
            continue
        url = "https://www.jwpepper.com" + href.split("?", 1)[0]
        if url in seen:
            continue
        seen.add(url)
        candidates.append(
            Candidate(
                url=url,
                label="Buy Sheet Music",
                source="JW Pepper link",
                title=title,
                metadata={},
            )
        )
        if len(candidates) >= 10:
            break
    return candidates


def extract_amazon_candidates(payload: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen_urls: set[str] = set()
    
    # Try multiple patterns to capture product links
    patterns = [
        # Standard product link pattern
        r'href="(/dp/[^"]+?)"[^>]*>([^<]+(?:<span[^>]*>[^<]+</span>[^<]*)*?)</a>',
        # Alternative with class selector
        r'<a[^>]+class="[^"]*a-link-normal[^"]*"[^>]+href="(?P<href>/[^"]+)"[^>]*>.*?<span[^>]*>(?P<title>.*?)</span>',
    ]
    
    for pattern_str in patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE | re.DOTALL)
        matches = list(pattern.finditer(payload))
        logging.debug("extract_amazon_candidates: pattern found %d matches", len(matches))
        
        for match in matches:
            try:
                if match.lastindex == 2:
                    # First pattern groups
                    href = match.group(1)
                    title = match.group(2)
                else:
                    # Named groups
                    href = match.group("href")
                    title = match.group("title")
                
                # Clean up title
                title = re.sub(r"<[^>]+>", " ", title)
                title = " ".join(title.split())
                
                if not href or not title or len(title) < 5:
                    continue
                
                # Only get actual product pages
                if not href.startswith("/dp/") and not href.startswith("/"):
                    continue
                if "/sspa/" in href or "/gp/slredirect" in href:
                    continue
                
                url = "https://www.amazon.com" + href.split("&", 1)[0] if href.startswith("/") else "https://www.amazon.com" + href
                
                if url not in seen_urls:
                    candidates.append(
                        Candidate(
                            url=url,
                            label="Buy Sheet Music",
                            source="Amazon link",
                            title=title,
                            metadata={},
                        )
                    )
                    seen_urls.add(url)
                    logging.debug("extract_amazon_candidates: added candidate: '%s'", title)
                    if len(candidates) >= 5:
                        break
            except Exception as e:
                logging.debug("extract_amazon_candidates: error processing match: %s", str(e))
                continue
        
        if candidates:
            break  # Stop trying patterns if we found candidates
    
    logging.debug("extract_amazon_candidates: returning %d candidates", len(candidates))
    return candidates


def extract_smp_candidates(payload: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    pattern = re.compile(
        r'<a[^>]+href="(?P<href>/en/product/[^"]+)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    seen: set[str] = set()
    for match in pattern.finditer(payload):
        href = match.group("href")
        title = re.sub(r"<[^>]+>", " ", match.group("title"))
        title = " ".join(title.split())
        if not href or not title or href in seen:
            continue
        seen.add(href)
        candidates.append(
            Candidate(
                url="https://www.sheetmusicplus.com" + href,
                label="Buy Sheet Music",
                source="Sheet Music Plus link",
                title=title,
                metadata={},
            )
        )
        if len(candidates) >= 5:
            break
    return candidates


def extract_musicnotes_candidates(payload: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    pattern = re.compile(
        r'<a[^>]+href="(?P<href>/sheetmusic/[^"#?]+[^"]*)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    seen: set[str] = set()
    for match in pattern.finditer(payload):
        href = match.group("href")
        title = re.sub(r"<[^>]+>", " ", match.group("title"))
        title = " ".join(title.split())
        if not href or not title:
            continue
        url = "https://www.musicnotes.com" + href
        if url in seen:
            continue
        seen.add(url)
        candidates.append(
            Candidate(
                url=url,
                label="Buy Sheet Music",
                source="Musicnotes link",
                title=title,
                metadata={},
            )
        )
        if len(candidates) >= 5:
            break
    return candidates


async def search_jwpepper(
    row: Any,
    instrument_slug: str,
    semaphore: asyncio.Semaphore,
) -> Candidate | None:
    def best_candidate(candidates: list[Candidate], threshold: int) -> Candidate | None:
        if not candidates:
            return None
        best = max(candidates, key=lambda candidate: score_candidate(row, instrument_slug, candidate))
        if score_candidate(row, instrument_slug, best) >= threshold:
            return best
        return None

    async def fetch_api_candidates(raw_query: str) -> list[Candidate]:
        sanitized_query = sanitize_jwpepper_query(raw_query)
        if not sanitized_query:
            return []
        payload = await fetch_with_retries(
            JWPEPPER_SEARCH_URL + quote_plus(sanitized_query),
            domain_semaphore=semaphore,
            min_delay=JWPEPPER_DELAY_MIN,
            max_delay=JWPEPPER_DELAY_MAX,
        )
        return extract_jwpepper_candidates(payload)

    for query in query_variants(row, instrument_slug):
        try:
            candidates = await fetch_api_candidates(query)
            if best := best_candidate(candidates, threshold=72):
                return best

            # Fallback: scrape JW Pepper's public site search when API candidates are weak/missing.
            sanitized_query = sanitize_jwpepper_query(query)
            web_payload = await fetch_with_retries(
                JWPEPPER_WEB_SEARCH_URL.format(query=quote_plus(sanitized_query)),
                domain_semaphore=semaphore,
                min_delay=JWPEPPER_DELAY_MIN,
                max_delay=JWPEPPER_DELAY_MAX,
            )
            web_candidates = extract_jwpepper_web_candidates(web_payload)
            if best := best_candidate(web_candidates, threshold=66):
                return best
        except Exception:
            continue

    # Some JW Pepper API phrase queries fail (HTTP 400). Retry with single-token queries.
    token_pool = list(title_tokens(row.title, row.publisher_text))
    composer_tokens = [
        token
        for token in normalize(row.composer).split()
        if token not in {"anon", "trad", "traditional", "various", "and"}
    ]
    token_pool.extend(composer_tokens)

    unique_tokens = sorted({token for token in token_pool if len(token) >= 4}, key=len, reverse=True)
    token_candidates: dict[str, Candidate] = {}
    for token in unique_tokens[:8]:
        try:
            for candidate in await fetch_api_candidates(token):
                token_candidates[candidate.url] = candidate
        except Exception:
            continue

    if best := best_candidate(list(token_candidates.values()), threshold=72):
        return best

    return None


async def search_amazon(
    row: Any,
    instrument_slug: str,
    semaphore: asyncio.Semaphore,
) -> Candidate | None:
    if amazon_is_temporarily_disabled():
        remaining = int(AMAZON_RATE_LIMIT_STATE.disabled_until_epoch - now_epoch())
        current = now_epoch()
        if current - AMAZON_RATE_LIMIT_STATE.last_cooldown_log_epoch >= 30:
            logging.info("Skipping Amazon during cooldown (%ss remaining)", max(0, remaining))
            AMAZON_RATE_LIMIT_STATE.last_cooldown_log_epoch = current
        return None

    query_list = query_variants(row, instrument_slug)
    for idx, query in enumerate(query_list):
        if amazon_is_temporarily_disabled():
            return None
        try:
            full_query = query + " sheet music"
            logging.debug("Amazon search for %s: trying query '%s'", row.code, full_query)
            payload = await fetch_with_retries(
                AMAZON_SEARCH_URL.format(query=quote_plus(full_query)),
                domain_semaphore=semaphore,
                min_delay=FALLBACK_DELAY_MIN,
                max_delay=FALLBACK_DELAY_MAX,
            )
            if is_amazon_rate_limit_payload(payload):
                mark_amazon_rate_limited("payload robot/captcha page")
                return None

            clear_amazon_rate_limit_signal()

            candidates = extract_amazon_candidates(payload)
            logging.debug("Amazon search for %s: found %d candidates", row.code, len(candidates))
            if not candidates:
                continue
            best = max(candidates, key=lambda candidate: score_candidate(row, instrument_slug, candidate))
            best_score = score_candidate(row, instrument_slug, best)
            logging.debug(
                "Amazon search for %s: best candidate score=%d, title='%s'",
                row.code,
                best_score,
                best.title,
            )
            # Lower threshold for Amazon - it's harder to match perfectly
            threshold = 75 if idx < 2 else 80
            if best_score >= threshold:
                logging.debug("Amazon search for %s: score meets threshold (>= %d)", row.code, threshold)
                return best
            else:
                logging.debug("Amazon search for %s: score too low (%d < %d)", row.code, best_score, threshold)
        except Exception as e:
            if is_amazon_rate_limit_exception(e):
                mark_amazon_rate_limited(str(e))
                return None
            logging.debug("Amazon search for %s: exception: %s", row.code, str(e))
            continue
    logging.debug("Amazon search for %s: no matches across %d queries", row.code, len(query_list))
    return None


async def search_musicnotes(
    row: Any,
    instrument_slug: str,
    semaphore: asyncio.Semaphore,
) -> Candidate | None:
    for query in query_variants(row, instrument_slug):
        try:
            payload = await fetch_with_retries(
                MUSICNOTES_SEARCH_URL.format(query=quote_plus(query)),
                domain_semaphore=semaphore,
                min_delay=FALLBACK_DELAY_MIN,
                max_delay=FALLBACK_DELAY_MAX,
            )
            candidates = extract_musicnotes_candidates(payload)
            if not candidates:
                continue
            best = max(candidates, key=lambda candidate: score_candidate(row, instrument_slug, candidate))
            if score_candidate(row, instrument_slug, best) >= 84:
                return best
        except Exception:
            continue
    return None


async def search_sheetmusicplus(
    row: Any,
    instrument_slug: str,
    semaphore: asyncio.Semaphore,
) -> Candidate | None:
    for query in query_variants(row, instrument_slug):
        try:
            payload = await fetch_with_retries(
                SMP_SEARCH_URL.format(query=quote_plus(query)),
                domain_semaphore=semaphore,
                min_delay=FALLBACK_DELAY_MIN,
                max_delay=FALLBACK_DELAY_MAX,
            )
            candidates = extract_smp_candidates(payload)
            if not candidates:
                continue
            best = max(candidates, key=lambda candidate: score_candidate(row, instrument_slug, candidate))
            if score_candidate(row, instrument_slug, best) >= 92:
                return best
        except Exception:
            continue
    return None


async def find_sheet_music(
    row: Any,
    instrument_slug: str,
    *,
    jwpepper_semaphore: asyncio.Semaphore,
    amazon_semaphore: asyncio.Semaphore,
    smp_semaphore: asyncio.Semaphore,
    musicnotes_semaphore: asyncio.Semaphore,
) -> Candidate | None:
    try:
        candidate = await search_jwpepper(row, instrument_slug, jwpepper_semaphore)
        if candidate:
            return candidate
    except Exception:
        pass

    if JWPEPPER_ONLY_MODE:
        return None

    try:
        candidate = await search_sheetmusicplus(row, instrument_slug, smp_semaphore)
        if candidate:
            return candidate
    except Exception:
        pass

    try:
        candidate = await search_musicnotes(row, instrument_slug, musicnotes_semaphore)
        if candidate:
            return candidate
    except Exception:
        pass

    try:
        candidate = await search_amazon(row, instrument_slug, amazon_semaphore)
        if candidate:
            return candidate
    except Exception:
        pass

    return None


async def process_instrument(
    instrument_slug: str,
    global_semaphore: asyncio.Semaphore,
    jwpepper_semaphore: asyncio.Semaphore,
    amazon_semaphore: asyncio.Semaphore,
    smp_semaphore: asyncio.Semaphore,
    musicnotes_semaphore: asyncio.Semaphore,
) -> dict[str, int]:
    config = INSTRUMENT_CONFIGS[instrument_slug]
    csv_path = config["csv_path"]
    cache_path = affiliate_cache_path_for_instrument(instrument_slug)
    attempts_path = attempt_cache_path_for_instrument(instrument_slug)
    cache = load_affiliate_links_cache(cache_path)
    attempt_cache = load_attempt_cache(attempts_path)
    rows = read_rows_from_csv(csv_path)

    if RESCAN_MODE == "reset":
        cache = {}
        attempt_cache = {}
        logging.info("%s: rescan mode 'reset' active (cleared cache + attempts in memory)", instrument_slug)

    if RESCAN_MODE in {"all", "reset"}:
        missing_rows = list(rows)
    else:
        missing_rows = [
            row
            for row in rows
            if row.code not in cache and row.code not in attempt_cache
        ]

    if ONLY_TEST_CODE:
        # In test mode, always re-attempt the code even if already cached.
        missing_rows = [row for row in rows if row.code == ONLY_TEST_CODE]

    logging.info(
        "Starting %s: %s total rows, %s missing links%s",
        instrument_slug,
        len(rows),
        len(missing_rows),
        f" (test code {ONLY_TEST_CODE})" if ONLY_TEST_CODE else "",
    )

    updated = 0
    failures = 0
    state_write_lock = asyncio.Lock()
    rows_since_flush = 0
    last_flush_epoch = now_epoch()
    pending_cache_write = False
    pending_attempt_write = False

    async def persist_state(
        *,
        write_cache: bool,
        write_attempts: bool,
        processed_row: bool = False,
        force: bool = False,
    ) -> None:
        nonlocal rows_since_flush, last_flush_epoch, pending_cache_write, pending_attempt_write
        async with state_write_lock:
            if processed_row:
                rows_since_flush += 1
            pending_cache_write = pending_cache_write or write_cache
            pending_attempt_write = pending_attempt_write or write_attempts

            should_flush = force or (
                rows_since_flush >= STATE_FLUSH_EVERY_ROWS
                or (now_epoch() - last_flush_epoch) >= STATE_FLUSH_EVERY_SECONDS
            )
            if not should_flush:
                return

            if pending_cache_write:
                cache_path.write_text(
                    json.dumps(dict(sorted(cache.items())), indent=2),
                    encoding="utf-8",
                )
            if pending_attempt_write:
                attempts_path.write_text(
                    json.dumps(dict(sorted(attempt_cache.items())), indent=2),
                    encoding="utf-8",
                )

            rows_since_flush = 0
            last_flush_epoch = now_epoch()
            pending_cache_write = False
            pending_attempt_write = False

    async def worker(row: Any) -> None:
        nonlocal updated, failures
        async with global_semaphore:
            try:
                candidate = await find_sheet_music(
                    row,
                    instrument_slug,
                    jwpepper_semaphore=jwpepper_semaphore,
                    amazon_semaphore=amazon_semaphore,
                    smp_semaphore=smp_semaphore,
                    musicnotes_semaphore=musicnotes_semaphore,
                )
                if not candidate:
                    failures += 1
                    attempt_cache[row.code] = {
                        "lastAttempted": datetime.now(timezone.utc).isoformat(),
                        "matched": False,
                    }
                    await persist_state(write_cache=False, write_attempts=True, processed_row=True)
                    logging.info("No match for %s %s", row.code, row.title)
                    return

                cache[row.code] = {
                    "url": candidate.url,
                    "label": candidate.label,
                    "source": candidate.source,
                    "lastChecked": datetime.now(timezone.utc).isoformat(),
                }
                attempt_cache[row.code] = {
                    "lastAttempted": datetime.now(timezone.utc).isoformat(),
                    "matched": True,
                    "source": candidate.source,
                }
                updated += 1
                logging.info(
                    "Matched %s %s -> %s (%s)",
                    row.code,
                    row.title,
                    candidate.url,
                    candidate.source,
                )
                await persist_state(write_cache=True, write_attempts=True, processed_row=True)
            except Exception as exc:
                failures += 1
                logging.exception("Unexpected error for %s %s: %s", row.code, row.title, exc)

    await asyncio.gather(*(worker(row) for row in missing_rows), return_exceptions=True)

    await persist_state(write_cache=True, write_attempts=True, force=True)

    # Rebuild the instrument JSON so the local site picks up the new links.
    try:
        build_from_csv(
            csv_path,
            school_year=DEFAULT_SCHOOL_YEAR,
            source_label="local CSV snapshots",
            instrument_slug=instrument_slug,
            affiliate_links=cache,
        )
    except Exception as exc:
        logging.exception("Build failed for %s: %s", instrument_slug, exc)

    logging.info(
        "Finished %s: added=%s missed=%s total_cache=%s",
        instrument_slug,
        updated,
        failures,
        len(cache),
    )
    return {
        "updated": updated,
        "failures": failures,
        "totalRows": len(rows),
        "missingAtStart": len(missing_rows),
        "cacheSize": len(cache),
        "attemptedSize": len(attempt_cache),
    }


async def main() -> None:
    setup_logging()
    logging.info("Bulk sheet music fill started")
    if RESCAN_MODE not in {"none", "all", "reset"}:
        logging.warning("Invalid SCAN_RESCAN_MODE '%s'; falling back to 'none'", RESCAN_MODE)
    logging.info(
        "Concurrency config: global=%s jwpepper=%s fallback=%s",
        GLOBAL_CONCURRENCY,
        JWPEPPER_CONCURRENCY,
        FALLBACK_CONCURRENCY,
    )
    logging.info(
        "Delay config: jwpepper=%s-%ss fallback=%s-%ss",
        JWPEPPER_DELAY_MIN,
        JWPEPPER_DELAY_MAX,
        FALLBACK_DELAY_MIN,
        FALLBACK_DELAY_MAX,
    )
    logging.info(
        "State flush config: every_rows=%s every_seconds=%s",
        STATE_FLUSH_EVERY_ROWS,
        STATE_FLUSH_EVERY_SECONDS,
    )
    logging.info("Rescan mode: %s", RESCAN_MODE if RESCAN_MODE in {"none", "all", "reset"} else "none")

    global_semaphore = asyncio.Semaphore(GLOBAL_CONCURRENCY)
    jwpepper_semaphore = asyncio.Semaphore(JWPEPPER_CONCURRENCY)
    amazon_semaphore = asyncio.Semaphore(FALLBACK_CONCURRENCY)
    smp_semaphore = asyncio.Semaphore(FALLBACK_CONCURRENCY)
    musicnotes_semaphore = asyncio.Semaphore(FALLBACK_CONCURRENCY)

    summary: dict[str, dict[str, int]] = {}
    for instrument_slug in INSTRUMENT_CONFIGS:
        try:
            summary[instrument_slug] = await process_instrument(
                instrument_slug,
                global_semaphore,
                jwpepper_semaphore,
                amazon_semaphore,
                smp_semaphore,
                musicnotes_semaphore,
            )
            if ONLY_TEST_CODE and summary[instrument_slug].get("missingAtStart", 0) > 0:
                logging.info("ONLY_TEST_CODE matched in %s; ending run after one code", instrument_slug)
                break
        except Exception as exc:
            logging.exception("Instrument-level failure for %s: %s", instrument_slug, exc)
            summary[instrument_slug] = {
                "updated": 0,
                "failures": 0,
                "totalRows": 0,
                "missingAtStart": 0,
                "cacheSize": 0,
            }

    logging.info("Bulk sheet music fill finished")
    logging.info("Summary: %s", json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
