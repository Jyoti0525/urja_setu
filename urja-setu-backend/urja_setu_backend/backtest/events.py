"""Curated labeled disruption events for the backtest.

Dates are drawn from public reporting of real Red Sea / Hormuz energy-supply
incidents (2024-2026). A denser, well-sourced ground-truth set makes the
precision/recall measurement fair: sparse labels punish the detector for
flagging real events that simply weren't in the list.

corridor must match a key in harness.TIMELINE_QUERIES.
"""

from __future__ import annotations

LABELED_EVENTS: list[dict] = [
    # --- Red Sea / Bab-el-Mandeb (near-continuous Houthi campaign) ---
    {"date": "2024-01-12", "corridor": "bab-el-mandeb", "note": "US/UK launch strikes on Houthi targets after Red Sea attacks"},
    {"date": "2024-01-26", "corridor": "bab-el-mandeb", "note": "Tanker Marlin Luanda hit by Houthi missile in Gulf of Aden"},
    {"date": "2024-02-18", "corridor": "bab-el-mandeb", "note": "MV Rubymar struck by Houthi missile (later sinks)"},
    {"date": "2024-03-06", "corridor": "bab-el-mandeb", "note": "True Confidence struck; first Red Sea seafarer deaths"},
    {"date": "2024-06-12", "corridor": "bab-el-mandeb", "note": "Bulker Tutor sunk after Houthi attack"},
    {"date": "2024-07-19", "corridor": "bab-el-mandeb", "note": "Houthi drone reaches Tel Aviv; Red Sea tensions spike"},
    {"date": "2024-08-21", "corridor": "bab-el-mandeb", "note": "Tanker Sounion set ablaze in the Red Sea"},
    {"date": "2024-09-02", "corridor": "bab-el-mandeb", "note": "Sounion salvage crisis; oil-spill threat"},
    {"date": "2024-11-11", "corridor": "bab-el-mandeb", "note": "Renewed Houthi strikes on shipping after lull"},
    {"date": "2025-03-15", "corridor": "bab-el-mandeb", "note": "US strikes on Houthis; shipping threat renewed"},
    {"date": "2025-07-07", "corridor": "bab-el-mandeb", "note": "Bulk carriers attacked/sunk in the Red Sea"},
    {"date": "2025-09-10", "corridor": "bab-el-mandeb", "note": "Escalating Houthi attacks on Red Sea shipping lanes"},
    {"date": "2026-03-05", "corridor": "bab-el-mandeb", "note": "Renewed Red Sea shipping disruption"},
    # --- Strait of Hormuz / Persian Gulf / Iran ---
    {"date": "2024-04-13", "corridor": "hormuz", "note": "Iran seizes MSC Aries near Hormuz; Iran-Israel strikes"},
    {"date": "2024-10-01", "corridor": "hormuz", "note": "Iran missile barrage on Israel; Gulf escalation fears"},
    {"date": "2024-10-26", "corridor": "hormuz", "note": "Israel strikes Iran; oil-facility risk in focus"},
    {"date": "2025-01-15", "corridor": "hormuz", "note": "Renewed US sanctions pressure on Iranian crude exports"},
    {"date": "2025-06-18", "corridor": "hormuz", "note": "US-Iran standoff; Hormuz closure threat; Brent +8% in a session"},
    {"date": "2025-06-23", "corridor": "hormuz", "note": "Iran parliament backs Hormuz closure option"},
    {"date": "2025-10-12", "corridor": "hormuz", "note": "Fresh sanctions wave on Iranian oil shipments"},
    {"date": "2026-01-20", "corridor": "hormuz", "note": "Persian Gulf maritime security incident; sanctions escalation"},
    {"date": "2026-04-02", "corridor": "hormuz", "note": "Gulf tanker incident raises Hormuz transit risk"},
]
