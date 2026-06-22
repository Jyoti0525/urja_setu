"""Live commodity price ingestion via yfinance (free). Brent crude = ticker BZ=F."""

from __future__ import annotations

import time

_TTL = 120.0
_cache: dict = {"ts": 0.0, "data": None}


def brent_snapshot() -> dict:
    """Latest Brent price + daily change % (cached 2 min). Fails soft to None values."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < _TTL:
        return _cache["data"]

    result = {"price": None, "change_pct": None, "prev_close": None}
    try:
        import yfinance as yf

        hist = yf.Ticker("BZ=F").history(period="5d")
        if hist is not None and not hist.empty:
            closes = hist["Close"].dropna()
            if not closes.empty:
                price = float(closes.iloc[-1])
                prev = float(closes.iloc[-2]) if len(closes) > 1 else price
                change = ((price - prev) / prev * 100.0) if prev else 0.0
                result = {
                    "price": round(price, 2),
                    "change_pct": round(change, 2),
                    "prev_close": round(prev, 2),
                }
    except Exception:
        pass

    if result["price"] is not None:
        _cache.update(ts=now, data=result)
    return result
