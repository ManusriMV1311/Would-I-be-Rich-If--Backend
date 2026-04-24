import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# In-memory dictionary cache tracking exact TTL expirations
_historical_cache = {}
CACHE_TTL = 86400  # 1 day TTL in seconds

def fetch_historical_data(ticker: str, start_date: str) -> list[dict]:
    """
    Fetch historical daily prices for a given asset, relying safely on a 1-day cache logic.
    """
    cache_key = f"{ticker}_{start_date}"
    now = time.time()
    
    # TTL Cache Validation Check
    if cache_key in _historical_cache and _historical_cache[cache_key]["expires_at"] > now:
        return _historical_cache[cache_key]["data"]

    try:
        asset = yf.Ticker(ticker)
        df = asset.history(start=start_date)

        if df.empty:
            raise ValueError(f"No data found for ticker '{ticker}'")

        # Normalize metrics and discard all columns except Close
        df = df[['Close']].copy()
        
        # Ensure index is timezone-naive to match all_dates
        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        df.index = df.index.normalize()

        today = datetime.today().strftime("%Y-%m-%d")
        all_dates = pd.date_range(start=start_date, end=today, freq='D')
        
        # Reindex and fill NaNs carefully
        df = df.reindex(all_dates)
        df = df.ffill().bfill() # Fill forward from available data, then backward for the start

        # Check for remaining NaNs (if ticker had NO data at all)
        if df['Close'].isna().all():
            raise ValueError(f"No valid price data found for ticker '{ticker}' in this range.")
        
        # Format output
        result = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"])
            }
            for date, row in df.iterrows()
        ]

        # Insert into live TTL cache
        _historical_cache[cache_key] = {"data": result, "expires_at": now + CACHE_TTL}

        return result

    except Exception as e:
        raise ValueError(f"Error fetching historical data: {str(e)}")

def fetch_live_price(ticker: str) -> float:
    """
    Fetches the instantaneous latest closing price. DO NOT CACHE under any circumstance.
    """
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period="1d")
        
        if df.empty:
            raise ValueError(f"No live data found for ticker '{ticker}'")
            
        return float(df['Close'].iloc[-1])
    except Exception as e:
        raise ValueError(f"Error fetching live price: {str(e)}")


def fetch_data(ticker: str, start_date: str) -> list[dict]:
    """Legacy Wrapper Endpoint, safely redirects to historical cache"""
    return fetch_historical_data(ticker, start_date)