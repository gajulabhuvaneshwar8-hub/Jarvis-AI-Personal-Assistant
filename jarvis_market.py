"""
jarvis_market.py - Real-Time Stock Market Intelligence & Buy/Sell Analysis
Connects to live market feeds (Yahoo Finance) for Indian & US stocks and Crypto.
"""

import urllib.request
import urllib.parse
import json
import ssl
import time

try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = None

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"

# Default Watchlist: Indian Bluechips, Indices, US Tech & Crypto
DEFAULT_TICKERS = {
    "^NSEI": "Nifty 50",
    "^BSESN": "Sensex",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "TCS",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "NVDA": "Nvidia",
    "AAPL": "Apple",
    "BTC-USD": "Bitcoin",
}


def _fetch_chart(symbol, range_period="5d", interval="15m"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range={range_period}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10, context=_CTX) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
            res = data.get("chart", {}).get("result", [])
            if not res:
                return None
            return res[0]
    except Exception as e:
        return None


def analyze_ticker(symbol):
    """
    Fetches real-time price, calculates 5-day momentum & moving average,
    and returns a Buy, Sell, or Hold signal with key levels.
    """
    chart = _fetch_chart(symbol)
    if not chart:
        return None

    meta = chart.get("meta", {})
    name = DEFAULT_TICKERS.get(symbol, symbol)
    currency = meta.get("currency", "INR" if ".NS" in symbol or "^" in symbol else "USD")
    curr_symbol = "₹" if currency == "INR" else "$"

    price = meta.get("regularMarketPrice")
    prev_close = meta.get("chartPreviousClose") or meta.get("previousClose") or price

    if price is None:
        return None

    change = price - prev_close
    pct_change = (change / prev_close) * 100 if prev_close else 0.0

    quotes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    valid_quotes = [q for q in quotes if q is not None]

    signal = "HOLD"
    reason = "Consolidating near previous close."

    if len(valid_quotes) >= 10:
        sma_short = sum(valid_quotes[-5:]) / 5.0
        sma_long = sum(valid_quotes[-15:]) / min(len(valid_quotes), 15)

        if price > sma_short and sma_short > sma_long and pct_change > 0.5:
            signal = "STRONG BUY"
            reason = "Bullish momentum above short-term and medium-term moving averages."
        elif price > sma_short and pct_change >= 0.0:
            signal = "BUY / ACCUMULATE"
            reason = "Holding above short-term support with positive price action."
        elif price < sma_short and sma_short < sma_long and pct_change < -0.5:
            signal = "STRONG SELL / SHORT"
            reason = "Bearish crossover below major moving averages with active selling pressure."
        elif price < sma_short:
            signal = "SELL / TAKE PROFIT"
            reason = "Slipping below intraday support; risk of further pullback."

    return {
        "symbol": symbol,
        "name": name,
        "price": round(price, 2),
        "change": round(change, 2),
        "pct_change": round(pct_change, 2),
        "currency": curr_symbol,
        "signal": signal,
        "reason": reason,
        "high": meta.get("regularMarketDayHigh", price),
        "low": meta.get("regularMarketDayLow", price),
    }


def market_briefing():
    """Returns a formatted spoken overview of major indices and top signals."""
    reports = []
    for sym in ["^NSEI", "RELIANCE.NS", "NVDA", "BTC-USD"]:
        data = analyze_ticker(sym)
        if data:
            direction = "up" if data["pct_change"] >= 0 else "down"
            reports.append(
                f"{data['name']} is at {data['currency']}{data['price']:,}, {direction} {abs(data['pct_change'])}%. Signal: {data['signal']}."
            )
    return " ".join(reports)


def get_market_watchlist():
    """Returns all watched tickers as structured data for the holographic HUD."""
    results = []
    for sym, name in DEFAULT_TICKERS.items():
        data = analyze_ticker(sym)
        if data:
            results.append(data)
    return results


if __name__ == "__main__":
    print("Testing Jarvis Market Intelligence...")
    print(market_briefing())
