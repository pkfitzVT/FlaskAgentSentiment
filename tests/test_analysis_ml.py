import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Functions under test, to be imported from your module.
# For demo, redefining here; in real use, replace with:
# from your_module import merge_data, fit_model, evaluate_model


def merge_data(df, next_price_df):
    merged = pd.merge(
        df, next_price_df, left_on="date", right_on="price_date", how="left"
    )
    merged["return"] = (merged["next_close"] / merged["close_price"]) - 1
    merged = merged.dropna(subset=["return"])
    return merged


def fit_model(df):
    X = df[["sentiment"]]
    y = df["return"]
    model = LinearRegression()
    model.fit(X, y)
    df["predicted_return"] = model.predict(X)
    return model, df


def evaluate_model(df):
    y = df["return"]
    y_pred = df["predicted_return"]
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    directional_acc = (np.sign(y_pred) == np.sign(y)).mean()
    return r2, mse, directional_acc


@pytest.fixture
def mock_data():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-06-10", periods=5, freq="D"),
            "sentiment": [0.9, 0.2, -0.3, 0.5, -0.7],
            "close_price": [100, 102, 98, 105, 103],
        }
    )
    next_price_df = pd.DataFrame(
        {
            "price_date": pd.date_range("2024-06-10", periods=5, freq="D"),
            "next_close": [102, 98, 105, 103, np.nan],  # No price for last date
        }
    )
    return df, next_price_df


def test_merge_data(mock_data):
    df, next_price_df = mock_data
    merged = merge_data(df, next_price_df)
    # Last row should drop (next_close = NaN)
    assert len(merged) == 4
    assert "return" in merged.columns
    # Quick check: first return value
    expected_return = (102 / 100) - 1  # 0.02
    assert np.isclose(merged["return"].iloc[0], expected_return)


def test_fit_model(mock_data):
    df, next_price_df = mock_data
    merged = merge_data(df, next_price_df)
    model, merged = fit_model(merged)
    assert hasattr(model, "predict")
    assert "predicted_return" in merged.columns
    # Check predicted shape
    assert len(merged["predicted_return"]) == len(merged["return"])


def test_evaluate_model(mock_data):
    df, next_price_df = mock_data
    merged = merge_data(df, next_price_df)
    _, merged = fit_model(merged)
    r2, mse, directional_acc = evaluate_model(merged)
    assert isinstance(r2, float)
    assert isinstance(mse, float)
    assert 0.0 <= directional_acc <= 1.0


def test_pipeline_end_to_end(mock_data):
    df, next_price_df = mock_data
    merged = merge_data(df, next_price_df)
    model, merged = fit_model(merged)
    r2, mse, directional_acc = evaluate_model(merged)
    print("\nEnd-to-end test result:")
    print(
        merged[
            [
                "date",
                "sentiment",
                "close_price",
                "next_close",
                "return",
                "predicted_return",
            ]
        ]
    )
    print(f"R²: {r2:.4f}, MSE: {mse:.6f}, Directional Accuracy: {directional_acc:.2%}")
    assert "predicted_return" in merged.columns
    assert len(merged) == 4
