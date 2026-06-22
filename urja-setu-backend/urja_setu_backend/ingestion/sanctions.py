"""Live sanctions exposure from the real OFAC SDN list.

We download OFAC's Specially Designated Nationals list, count oil-relevant program
designations per producer country, and gate each corridor's exposure on whether the
program is genuinely active — so if OFAC adds/removes a program, our risk follows.
Cached 24h; fails soft to a curated assumption so it never breaks the demo.
"""

from __future__ import annotations

import csv
import io
import json
import time
from pathlib import Path

import httpx

SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
_SUMMARY_PATH = DATA_DIR / "ofac_summary.json"
_TTL = 24 * 3600

# OFAC program tag (substring) -> oil-producing country it sanctions.
PROGRAM_COUNTRY: dict[str, str] = {
    "IRAN": "Iran",
    "IFSR": "Iran",
    "IRGC": "Iran",
    "RUSSIA-EO14024": "Russia",
    "UKRAINE-EO13662": "Russia",
    "VENEZUELA": "Venezuela",
}

# Producer exposure feeding each corridor.
CORRIDOR_PRODUCERS: dict[str, list[tuple[str, float]]] = {
    "hormuz": [("Iran", 0.85)],
    "bab-el-mandeb": [("Iran", 0.5)],  # Houthi-Iran nexus on Red Sea transit
    "cape-good-hope": [],
    "malacca": [],
}


def _load_cache() -> dict | None:
    if _SUMMARY_PATH.exists():
        try:
            s = json.loads(_SUMMARY_PATH.read_text(encoding="utf-8"))
            if time.time() - s.get("ts", 0) < _TTL:
                return s
        except Exception:
            return None
    return None


def fetch_program_counts(*, timeout: float = 30.0) -> dict:
    """Return {'counts': {country: n}, 'source': ...}. Cached 24h; fails soft."""
    cached = _load_cache()
    if cached:
        return cached

    counts: dict[str, int] = {}
    source = "OFAC SDN (live)"
    try:
        r = httpx.get(
            SDN_URL,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "urja-setu/0.1 (hackathon PoC)"},
        )
        r.raise_for_status()
        for row in csv.reader(io.StringIO(r.text)):
            if len(row) < 4:
                continue
            program = (row[3] or "").upper()
            for tag, country in PROGRAM_COUNTRY.items():
                if tag in program:
                    counts[country] = counts.get(country, 0) + 1
                    break
    except Exception:
        # Fall back to a curated assumption (-1 = active but count unknown).
        counts = {"Iran": -1, "Russia": -1, "Venezuela": -1}
        source = "OFAC SDN (curated fallback)"

    summary = {"ts": time.time(), "counts": counts, "source": source}
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _SUMMARY_PATH.write_text(json.dumps(summary), encoding="utf-8")
    except Exception:
        pass
    return summary


def active_countries() -> set[str]:
    counts = fetch_program_counts()["counts"]
    return {c for c, n in counts.items() if n != 0}


def corridor_exposure() -> dict[str, float]:
    """{corridor_id: exposure 0..1}, gated on live OFAC program activity."""
    active = active_countries()
    out: dict[str, float] = {}
    for cid, producers in CORRIDOR_PRODUCERS.items():
        exposure = 0.0
        for country, weight in producers:
            if country in active:
                exposure = max(exposure, weight)
        out[cid] = exposure
    return out


def summary() -> dict:
    return fetch_program_counts()
