"""Strategic Petroleum Reserve (SPR) drawdown optimiser.

Deterministic decision-support: given the supply gap and when the first alternative
cargo arrives, compute the optimal reserve drawdown schedule that holds supply
constant until rerouted barrels ramp in — and whether reserves are sufficient.
"""

from __future__ import annotations

RAMP_DAYS = 5  # days for alternative cargoes to ramp from arrival to full gap coverage


def optimize(
    supply_gap_kbd: float,
    first_reroute_days: float,
    *,
    spr_days_total: float = 9.5,
    imports_kbd: float = 4700.0,
    horizon_days: int = 45,
) -> dict:
    """Return an SPR drawdown plan (schedule + verdict)."""
    reserve_total = spr_days_total * imports_kbd  # total reserve volume, kbd-days
    reserve = reserve_total
    schedule: list[dict] = []
    depletion_day: int | None = None

    for day in range(0, horizon_days + 1):
        if day < first_reroute_days:
            draw = supply_gap_kbd
        else:
            ramp = min(1.0, (day - first_reroute_days) / RAMP_DAYS)
            draw = supply_gap_kbd * (1.0 - ramp)
        reserve = max(0.0, reserve - draw)
        schedule.append({"day": day, "drawdown_kbd": round(draw, 1), "reserve_kbd_days": round(reserve, 0)})
        if reserve <= 0 and depletion_day is None:
            depletion_day = day
            break

    days_to_full_coverage = round(first_reroute_days + RAMP_DAYS, 1)
    reserve_pct = round(reserve / reserve_total * 100, 1) if reserve_total else 0.0

    if depletion_day is None:
        verdict = (
            f"Reserves bridge to full reroute coverage (day {days_to_full_coverage}) "
            f"with {reserve_pct}% of strategic stock to spare."
        )
    else:
        verdict = (
            f"Reserves insufficient — deplete on day {depletion_day}. "
            "Accelerate procurement or trigger demand-management."
        )

    return {
        "reserve_initial_kbd_days": round(reserve_total, 0),
        "peak_drawdown_kbd": round(supply_gap_kbd, 1),
        "first_reroute_days": round(first_reroute_days, 1),
        "days_to_full_coverage": days_to_full_coverage,
        "reserve_remaining_kbd_days": round(reserve, 0),
        "reserve_remaining_pct": reserve_pct,
        "depletion_day": depletion_day,
        "verdict": verdict,
        "schedule": schedule,
    }
