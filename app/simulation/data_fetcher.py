import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_data(ticker: str, start_date: str) -> list[dict]:
    """
    Fetch historical daily prices for a given asset.

    Args:
        ticker (str): Asset ticker (e.g., 'AAPL', 'BTC-USD')
        start_date (str): Start date in 'YYYY-MM-DD'

    Returns:
        List[Dict]: [{ "date": "YYYY-MM-DD", "price": float }]
    """

    try:
        asset = yf.Ticker(ticker)
        df = asset.history(start=start_date)

        if df.empty:
            raise ValueError(f"No data found for ticker '{ticker}'")

        # Keep only closing price
        df = df[['Close']].copy()

        # Normalize dates (remove time + timezone)
        df.index = df.index.normalize().tz_localize(None)

        # Create full date range (fill missing days)
        today = datetime.today().strftime("%Y-%m-%d")
        all_dates = pd.date_range(start=start_date, end=today, freq='D')

        df = df.reindex(all_dates).ffill().bfill()

        # Convert to required format
        result = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "price": float(row["Close"])
            }
            for date, row in df.iterrows()
        ]

        return result

    except Exception as e:
        raise ValueError(f"Error fetching data: {str(e)}")