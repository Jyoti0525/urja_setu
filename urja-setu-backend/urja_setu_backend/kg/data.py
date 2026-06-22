"""Curated knowledge-graph data: crude sources, routes, refinery acceptance.

Sources carry the corridor/chokepoint their tanker route to India transits, so the
Procurement Orchestrator can exclude a blocked corridor and rank real alternatives.
Figures are curated/illustrative (EIA crude assays, typical VLCC voyage days).
"""

from __future__ import annotations

# Each source: route to India (Jamnagar/west coast) transits `corridor`.
CRUDE_SOURCES: list[dict] = [
    {"id": "iraq-basrah", "country": "Iraq", "grade": "Basrah", "spot_usd": 80.1, "corridor": "hormuz", "transit_days": 12},
    {"id": "saudi-arabheavy", "country": "Saudi Arabia", "grade": "Arab Heavy", "spot_usd": 81.4, "corridor": "hormuz", "transit_days": 13},
    {"id": "uae-murban", "country": "UAE", "grade": "Murban", "spot_usd": 82.0, "corridor": "hormuz", "transit_days": 10},
    {"id": "kuwait-kec", "country": "Kuwait", "grade": "Kuwait Export", "spot_usd": 80.8, "corridor": "hormuz", "transit_days": 11},
    {"id": "russia-urals", "country": "Russia", "grade": "Urals", "spot_usd": 68.2, "corridor": "bab-el-mandeb", "transit_days": 22},
    {"id": "us-wti", "country": "USA", "grade": "WTI Midland", "spot_usd": 83.0, "corridor": "cape-good-hope", "transit_days": 38},
    {"id": "nigeria-bonny", "country": "Nigeria", "grade": "Bonny Light", "spot_usd": 84.6, "corridor": "cape-good-hope", "transit_days": 22},
    {"id": "angola-cabinda", "country": "Angola", "grade": "Cabinda", "spot_usd": 83.2, "corridor": "cape-good-hope", "transit_days": 21},
    {"id": "brazil-tupi", "country": "Brazil", "grade": "Tupi", "spot_usd": 82.1, "corridor": "cape-good-hope", "transit_days": 33},
    {"id": "guyana-liza", "country": "Guyana", "grade": "Liza", "spot_usd": 82.8, "corridor": "cape-good-hope", "transit_days": 30},
]

FREIGHT_USD_PER_DAY = 0.22  # $/bbl per voyage day (curated VLCC economics)

# Refinery crude acceptance (richer config for procurement matching).
REFINERY_SLATES: dict[str, set[str]] = {
    "jamnagar": {"Arab Heavy", "Basrah", "Urals", "WTI Midland", "Bonny Light", "Cabinda", "Tupi", "Murban"},
    "vadinar": {"Arab Medium", "Urals", "Basrah", "Bonny Light", "Cabinda"},
    "mangalore": {"Arab Light", "Arab Heavy", "Basrah", "Murban"},
    "paradip": {"Basrah Heavy", "Arab Heavy", "Urals", "Liza"},
    "visakh": {"Arab Light", "Urals", "WTI Midland"},
}

# Refineries most exposed to a corridor disruption (whose feedstock transits it).
CORRIDOR_REFINERIES: dict[str, list[str]] = {
    "hormuz": ["jamnagar", "vadinar", "mangalore"],
    "bab-el-mandeb": ["paradip", "visakh"],
    "cape-good-hope": [],
    "malacca": ["paradip", "visakh"],
}

ROUTE_LABEL: dict[str, str] = {
    "hormuz": "Strait of Hormuz",
    "bab-el-mandeb": "Red Sea / Suez",
    "cape-good-hope": "Cape of Good Hope",
    "malacca": "Strait of Malacca",
}
