"""GDELT DOC 2.0 ingestion — free, keyless global news/event feed.

GDELT rate-limits to ~1 request / 5s, so we make ONE broad query for energy /
chokepoint disruption news, then bucket articles to corridors locally by keyword.
A short TTL cache keeps repeated live calls fast and rate-limit-safe. GDELT is
intentionally noisy — the Risk Agent (LLM) relevance-filters and grades downstream.
"""

from __future__ import annotations

import time

import httpx

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

_BROAD_QUERY = (
    '(oil OR crude OR tanker OR OPEC OR refinery) '
    '(Hormuz OR "Red Sea" OR Houthi OR "Strait of Malacca" OR Suez OR '
    '"Cape of Good Hope" OR sanctions OR Iran) sourcelang:english'
)

# Keyword buckets to route a headline to one or more corridors.
CORRIDOR_KEYWORDS: dict[str, list[str]] = {
    "hormuz": ["hormuz", "persian gulf", "strait of hormuz", "iran", "gulf"],
    "bab-el-mandeb": ["red sea", "bab-el-mandeb", "bab el mandeb", "houthi", "aden", "yemen"],
    "cape-good-hope": ["cape of good hope", "suez", "reroute"],
    "malacca": ["malacca", "strait of malacca", "singapore strait"],
}

_TTL_SECONDS = 600.0  # reuse last good fetch for 10 min (rate-limit-safe across refreshes)
_cache: dict = {"ts": 0.0, "articles": []}


def fetch_all(*, timespan: str = "72h", max_records: int = 40, timeout: float = 15.0) -> list[dict]:
    """One broad GDELT query (cached, retries once on 429). Fails soft to last good result."""
    now = time.time()
    if now - _cache["ts"] < _TTL_SECONDS and _cache["articles"]:
        return _cache["articles"]

    params = {
        "query": _BROAD_QUERY,
        "mode": "ArtList",
        "maxrecords": max_records,
        "format": "json",
        "timespan": timespan,
        "sort": "DateDesc",
    }
    headers = {"User-Agent": "urja-setu/0.1 (hackathon PoC)"}

    data = None
    for attempt in range(2):
        try:
            resp = httpx.get(GDELT_URL, params=params, timeout=timeout, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                break
            # GDELT throttles to ~1 req / 5s — back off once then retry.
            if resp.status_code == 429 and attempt == 0:
                time.sleep(5)
                continue
            return _cache["articles"]
        except Exception:
            return _cache["articles"]
    if data is None:
        return _cache["articles"]

    articles: list[dict] = []
    for a in data.get("articles", []) or []:
        title = (a.get("title") or "").strip()
        if not title:
            continue
        articles.append(
            {
                "title": title,
                "url": a.get("url", ""),
                "domain": a.get("domain", ""),
                "seendate": a.get("seendate", ""),
                "sourcecountry": a.get("sourcecountry", ""),
            }
        )

    _cache.update(ts=now, articles=articles)
    return articles


def bucket_by_corridor(articles: list[dict]) -> dict[str, list[dict]]:
    """Assign each article to the corridors whose keywords appear in its title/domain."""
    out: dict[str, list[dict]] = {cid: [] for cid in CORRIDOR_KEYWORDS}
    for a in articles:
        text = f'{a["title"]} {a.get("domain", "")}'.lower()
        for cid, keywords in CORRIDOR_KEYWORDS.items():
            if any(k in text for k in keywords):
                out[cid].append(a)
    return out


def fetch_for_corridor(corridor_id: str) -> list[dict]:
    """Convenience: articles for a single corridor (uses the cached broad fetch)."""
    return bucket_by_corridor(fetch_all()).get(corridor_id, [])
