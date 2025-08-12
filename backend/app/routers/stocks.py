from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
import hashlib
from math import sin

import yfinance as yf
import pandas as pd

router = APIRouter(prefix="/api", tags=["stocks"])

# ---------- Fallback stub (kept for resilience) ----------
def stub_prices_for_ticker(ticker: str, days: int):
    h = int(hashlib.sha256(ticker.encode()).hexdigest()[:6], 16)
    base_price = 80 + (h % 120)         # ~80–200
    drift = ((h % 7) - 3) * 0.0002      # small bias
    data = []
    price = float(base_price)
    start = datetime.utcnow() - timedelta(days=days)
    for i in range(days):
        price *= (1.0 + drift + 0.0015 * sin((i + (h % 31)) / 9.0))
        o = round(price * 0.995, 2)
        hi = round(price * 1.01, 2)
        lo = round(price * 0.99, 2)
        c = round(price, 2)
        v = 150000 + ((i + h) % 200000)
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        data.append({"date": d, "open": o, "high": hi, "low": lo, "close": c, "volume": v})
    return data

def nse_symbol(ticker: str) -> str:
    t = ticker.upper()
    return t if t.endswith(".NS") else f"{t}.NS"

# ---------- Real price endpoint via Yahoo Finance ----------
@router.get("/stock/{ticker}/price")
def get_price(ticker: str, range: Optional[str] = Query("5y", pattern="^(1y|3y|5y)$")):
    period_map = {"1y": "1y", "3y": "3y", "5y": "5y"}
    period = period_map.get(range, "5y")
    sym = nse_symbol(ticker)

    try:
        df = yf.download(sym, period=period, interval="1d", auto_adjust=False, progress=False)
        if df is None or df.empty:
            # fallback to stub if empty
            days = {"1y": 365, "3y": 365*3, "5y": 365*5}[range]
            return {"ticker": ticker.upper(), "range": range, "series": stub_prices_for_ticker(ticker.upper(), days)}

        df = df.reset_index()  # columns: Date, Open, High, Low, Close, Adj Close, Volume
        series = []
        for _, row in df.iterrows():
            d = pd.to_datetime(row["Date"]).strftime("%Y-%m-%d")
            series.append({
                "date": d,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0
            })
        return {"ticker": ticker.upper(), "range": range, "series": series}

    except Exception:
        # keep the UI alive if Yahoo fails/rate-limits
        days = {"1y": 365, "3y": 365*3, "5y": 365*5}[range]
        return {"ticker": ticker.upper(), "range": range, "series": stub_prices_for_ticker(ticker.upper(), days)}

@router.get("/stock/{ticker}/fundamentals")
def get_fundamentals(ticker: str):
    return {
        "ticker": ticker.upper(),
        "market_cap": 250_000_000_000,
        "pe": 24.3,
        "roe": 18.7,
        "eps_ttm": 52.4,
        "debt_to_equity": 0.12,
        "updated": datetime.utcnow().isoformat()
    }

@router.get("/stock/{ticker}/news")
def get_news(ticker: str):
    now = datetime.utcnow()
    items = []
    for i in range(5):
        items.append({
            "title": f"{ticker.upper()} headline {i+1}",
            "source": "StubWire",
            "published_at": (now - timedelta(hours=(i+1)*5)).isoformat(),
            "url": "https://example.com/article"
        })
    return {"ticker": ticker.upper(), "items": items}