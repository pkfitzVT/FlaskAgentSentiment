# app/agents/stock_prices.py
"""
Module for fetching and upserting stock price data into Postgres.
"""
from datetime import timedelta

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

from app.agents.db_writer import StockPrice, upsert_stock_price

# Ensure environment variables are loaded
load_dotenv()


def fetch_and_store_stock(session, symbol: str, dt: pd.Timestamp.date) -> StockPrice:
    """
    Fetches the stock price for symbol on date dt and upserts into DB.
    Returns the StockPrice ORM object or None if no data.
    """
    # Use yfinance Ticker.history for reliable data
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=dt, end=dt + timedelta(days=1), auto_adjust=False)
    if data.empty:
        return None

    # Extract the first row
    row = data.iloc[0]

    # Read expected columns
    try:
        open_p = float(row["Open"])
        high_p = float(row["High"])
        low_p = float(row["Low"])
        close_p = float(row["Close"])
        volume = int(row["Volume"])
    except KeyError as e:
        raise KeyError(
            f"Expected column {e.args[0]} in stock history data; "
            f"available columns: {list(data.columns)}"
        )

    # Upsert via db_writer
    return upsert_stock_price(
        session,
        price_date=dt,
        open_p=open_p,
        close_p=close_p,
        high_p=high_p,
        low_p=low_p,
        volume=volume,
    )
