import pandas as pd

from app.agents.db_writer import Article, get_session
from app.agents.stock_prices import fetch_and_store_stock

session = get_session()
dates = session.query(Article.publish_date).distinct().all()
dates = [d[0] for d in dates]

symbol = "NVDA"  # Or your stock ticker

for dt in dates:
    print(f"Fetching price for {dt}")
    try:
        fetch_and_store_stock(session, symbol, pd.Timestamp(dt))
    except Exception as e:
        print(f"Could not fetch or insert price for {dt}: {e}")
