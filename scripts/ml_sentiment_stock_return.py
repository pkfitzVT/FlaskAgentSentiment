import numpy as np
import pandas as pd
from dotenv import load_dotenv

from app.agents.db_writer import Analysis, Article, StockPrice, get_session

load_dotenv()


def load_article_sentiment_prices(session):
    rows = (
        session.query(
            Article.publish_date,
            Analysis.sentiment_score,
            Analysis.sentiment_label,
            Analysis.recommendation,
            StockPrice.close_price,
        )
        .join(Analysis, Article.article_id == Analysis.article_id)
        .join(StockPrice, StockPrice.price_date == Article.publish_date)
        .order_by(Article.publish_date)
        .all()
    )

    # Build the DataFrame with raw score & label
    df = pd.DataFrame(
        rows,
        columns=[
            "date",
            "sentiment_score",
            "sentiment_label",
            "recommendation",
            "close_price",
        ],
    )

    # Overwrite `sentiment` to be the signed score
    df["sentiment"] = df["sentiment_score"] * df["sentiment_label"].map(
        {"POSITIVE": 1, "NEGATIVE": -1}
    )

    # Drop the now‐unneeded raw columns
    df = df.drop(columns=["sentiment_score", "sentiment_label"])

    return df


def load_next_day_prices(session):
    """
    Load closing prices and compute next day's closing price for each date.
    """
    rows = (
        session.query(StockPrice.price_date, StockPrice.close_price)
        .order_by(StockPrice.price_date)
        .all()
    )
    df = pd.DataFrame(rows, columns=["price_date", "next_close_price"])
    df["next_date"] = df["price_date"].shift(-1)
    df["next_close"] = df["next_close_price"].shift(-1)
    return df[["price_date", "next_close"]]


def merge_data(df, next_price_df):
    """
    Merge article/sentiment/price data with next day's price.
    """
    merged = pd.merge(
        df, next_price_df, left_on="date", right_on="price_date", how="left"
    )
    merged["return"] = (merged["next_close"] / merged["close_price"]) - 1
    merged = merged.dropna(subset=["return"])
    return merged


def fit_model(df):
    """
    Fit linear regression model to predict next-day return from sentiment.
    """
    from sklearn.linear_model import LinearRegression

    X = df[["sentiment"]]
    y = df["return"]
    model = LinearRegression()
    model.fit(X, y)
    df["predicted_return"] = model.predict(X)
    return model, df


def evaluate_model(df):
    """
    Evaluate model with R², MSE, and directional accuracy.
    """
    from sklearn.metrics import mean_squared_error, r2_score

    y = df["return"]
    y_pred = df["predicted_return"]
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    directional_acc = (np.sign(y_pred) == np.sign(y)).mean()
    return r2, mse, directional_acc


def main():
    session = get_session()
    article_df = load_article_sentiment_prices(session)
    next_price_df = load_next_day_prices(session)
    df = merge_data(article_df, next_price_df)
    model, df = fit_model(df)
    r2, mse, directional_acc = evaluate_model(df)
    return {
        "r2": r2,
        "mse": mse,
        "directional_accuracy": directional_acc,
        "df": df,  # Ready for your route to extract columns as lists
    }


if __name__ == "__main__":
    results = main()
    # Optionally, print some summary for CLI use
    print(
        f"R²: {results['r2']:.4f}, "
        f"MSE: {results['mse']:.6f}, "
        f"Directional Accuracy: {results['directional_accuracy']:.2%}"
    )
