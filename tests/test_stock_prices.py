import pandas as pd
import pytest

from app.agents import stock_prices


class DummyTicker:
    def __init__(self, data):
        self._data = data

    def history(self, start, end, auto_adjust=False):
        # ignore start/end for simplicity
        return self._data


class DummySession:
    pass


def test_empty_history_returns_none(monkeypatch):
    # Arrange: ticker.history returns empty DataFrame
    empty_df = pd.DataFrame()
    monkeypatch.setattr(stock_prices.yf, "Ticker", lambda symbol: DummyTicker(empty_df))

    # Act
    result = stock_prices.fetch_and_store_stock(
        DummySession(), "FAKE", pd.Timestamp("2025-06-18").date()
    )

    # Assert
    assert result is None


def test_missing_column_raises_key_error(monkeypatch):
    # Arrange: DataFrame missing “Open” column
    df = pd.DataFrame([{"High": 1, "Low": 1, "Close": 1, "Volume": 1}])
    monkeypatch.setattr(stock_prices.yf, "Ticker", lambda symbol: DummyTicker(df))

    # Act & Assert
    with pytest.raises(KeyError) as exc:
        stock_prices.fetch_and_store_stock(
            DummySession(), "FAKE", pd.Timestamp("2025-06-18").date()
        )
    assert "Expected column Open" in str(exc.value)


def test_successful_upsert_calls_db_writer(monkeypatch):
    # Arrange: a valid row
    data = pd.DataFrame(
        [{"Open": 10.5, "High": 11.0, "Low": 10.0, "Close": 10.8, "Volume": 1000}]
    )
    monkeypatch.setattr(stock_prices.yf, "Ticker", lambda symbol: DummyTicker(data))

    called = {}

    def fake_upsert(session, price_date, open_p, close_p, high_p, low_p, volume):
        called.update(locals())
        return "DB_OBJ"

    monkeypatch.setattr(stock_prices, "upsert_stock_price", fake_upsert)

    # Act
    dt = pd.Timestamp("2025-06-18").date()
    result = stock_prices.fetch_and_store_stock(DummySession(), "FAKE", dt)

    # Assert
    assert result == "DB_OBJ"
    assert called["price_date"] == dt
    assert called["open_p"] == 10.5
    assert called["high_p"] == 11.0
    assert called["low_p"] == 10.0
    assert called["close_p"] == 10.8
    assert called["volume"] == 1000
