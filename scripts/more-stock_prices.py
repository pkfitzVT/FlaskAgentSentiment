import yfinance as yf
from dotenv import load_dotenv

from app.agents.db_writer import get_session, upsert_stock_price

load_dotenv()

symbol = "NVDA"
# Choose a sensible window
start = "2024-01-01"
end = "2025-06-20"

df = yf.download(symbol, start=start, end=end)

session = get_session()

for dt, row in df.iterrows():
    upsert_stock_price(
        session,
        price_date=dt.date(),
        open_p=float(row["Open"]),
        close_p=float(row["Close"]),
        high_p=float(row["High"]),
        low_p=float(row["Low"]),
        volume=float(row["Volume"]),
    )
print("Stock price backfill complete!")
