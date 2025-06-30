import numpy as np
import pandas as pd
from flask import Blueprint, abort, render_template
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score
from sklearn.tree import DecisionTreeClassifier

from app.agents.db_writer import Analysis, Article, get_session
from scripts.ml_sentiment_stock_return import main

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    return "<h2>Welcome! Try <a href='/browse'>Browse Data</a>.</h2>"


# ---------- browse ----------
@bp.route("/browse")
def browse():
    session = get_session()
    rows = (
        session.query(
            Article.publish_date,
            Article.title,
            Analysis.sentiment_score,
            Analysis.recommendation,
            Article.article_id,
        )
        .join(Analysis)
        .order_by(Article.publish_date.desc())
        .all()
    )
    return render_template("browse.html", rows=rows)


# ---------- single-article ----------
@bp.route("/article/<int:aid>")
def article(aid):
    session = get_session()
    art = session.query(Article).get(aid) or abort(404)
    return render_template("article.html", art=art)


# ---------- analyze ----------
@bp.route("/analyze")
def analyze():
    results = main()
    df = results["df"]

    df["date"] = pd.to_datetime(df["date"])
    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    prices = df["close_price"].astype(float).tolist()
    sentiments = df["sentiment"].astype(float).tolist()
    actual_returns = df["return"].astype(float).tolist()
    predicted_returns = df["predicted_return"].astype(float).tolist()

    X = np.arange(len(dates), dtype=float)

    # ---- PRICE TREND ----
    arr_prices = np.array(prices, dtype=float)
    mask_price = np.isfinite(arr_prices)
    X_price = X[mask_price]
    y_price = arr_prices[mask_price]
    full_price_trend = [np.nan] * len(X)
    if len(y_price) >= 2:
        price_model = LinearRegression().fit(X_price.reshape(-1, 1), y_price)
        price_trend = price_model.predict(X_price.reshape(-1, 1)).tolist()
        for idx, val in zip(np.where(mask_price)[0], price_trend):
            full_price_trend[idx] = val
        price_r2 = r2_score(y_price, price_trend)
        price_coef = float(price_model.coef_[0])
        price_intercept = float(price_model.intercept_)
        slope, intercept, r_value, price_p_value, std_err = linregress(X_price, y_price)
        if price_p_value is not None and np.isfinite(price_p_value):
            price_p_value_str = f"{price_p_value:.3g}"
        else:
            price_p_value_str = "N/A"
    else:
        price_r2 = price_coef = price_intercept = float("nan")
        price_p_value_str = "N/A"

    # ---- SENTIMENT TREND ----
    arr_sentiments = np.array(sentiments, dtype=float)
    mask_sentiment = np.isfinite(arr_sentiments)
    X_sent = X[mask_sentiment]
    y_sent = arr_sentiments[mask_sentiment]
    full_sentiment_trend = [np.nan] * len(X)
    if len(y_sent) >= 2:
        sentiment_model = LinearRegression().fit(X_sent.reshape(-1, 1), y_sent)
        sentiment_trend = sentiment_model.predict(X_sent.reshape(-1, 1)).tolist()
        for idx, val in zip(np.where(mask_sentiment)[0], sentiment_trend):
            full_sentiment_trend[idx] = val
        sentiment_r2 = r2_score(y_sent, sentiment_trend)
        sentiment_coef = float(sentiment_model.coef_[0])
        sentiment_intercept = float(sentiment_model.intercept_)
    else:
        sentiment_r2 = sentiment_coef = sentiment_intercept = float("nan")

    # ---- LOGISTIC REGRESSION: LLM Rec vs. Next-Day Direction ----
    rec_map = {"strong_sell": -2, "sell": -1, "hold": 0, "buy": 1, "strong_buy": 2}
    df["rec_score"] = df["recommendation"].map(rec_map)
    df["return_up"] = (df["return"] > 0).astype(int)
    logit_df = df.dropna(subset=["rec_score"])

    X_logit = logit_df[["rec_score"]]
    y_logit = logit_df["return_up"]

    # 1) Base logistic model
    logit = LogisticRegression()
    logit.fit(X_logit, y_logit)
    y_logit_pred = logit.predict(X_logit)

    logit_accuracy = accuracy_score(y_logit, y_logit_pred)
    logit_confmat = confusion_matrix(y_logit, y_logit_pred)
    logit_coef = float(logit.coef_[0][0])
    logit_intercept = float(logit.intercept_[0])

    # 2) VIX-enhanced decision tree
    # ⚠️ Make sure df["vix_close"] exists at this point
    median_vix = df["vix_close"].median()
    df["strongbuy_and_lowvol"] = (
        (df["recommendation"] == "strong_buy") & (df["vix_close"] < median_vix)
    ).astype(int)

    X_vix = df[["strongbuy_and_lowvol"]]
    y_vix = df["return_up"]

    tree_vix = DecisionTreeClassifier(max_depth=3, random_state=42)
    tree_vix.fit(X_vix, y_vix)
    y_vix_pred = tree_vix.predict(X_vix)
    confmat_vix = confusion_matrix(y_vix, y_vix_pred)

    return render_template(
        "analyze.html",
        dates=dates,
        prices=prices,
        price_trend=full_price_trend,
        price_r2=price_r2,
        price_coef=price_coef,
        price_intercept=price_intercept,
        price_p_value_str=price_p_value_str,
        sentiments=sentiments,
        sentiment_trend=full_sentiment_trend,
        sentiment_r2=sentiment_r2,
        sentiment_coef=sentiment_coef,
        sentiment_intercept=sentiment_intercept,
        actual_returns=actual_returns,
        predicted_returns=predicted_returns,
        r2=results["r2"],
        mse=results["mse"],
        directional_accuracy=results["directional_accuracy"],
        # Logistic regression results
        logit_accuracy=logit_accuracy,
        logit_coef=logit_coef,
        logit_intercept=logit_intercept,
        confmat_base=logit_confmat.tolist(),  # renamed to match template
        confmat_vix=confmat_vix.tolist(),
    )
