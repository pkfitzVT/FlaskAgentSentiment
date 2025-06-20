# app/web/routes.py
import pandas as pd
from flask import Blueprint, abort, render_template

from app.agents.db_writer import Analysis, Article, get_session
from scripts.ml_sentiment_stock_return import main  # Import your main function

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


@bp.route("/analyze")
def analyze():
    results = main()
    df = results["df"]

    # Ensure 'date' is datetime (fixes your error!)
    df["date"] = pd.to_datetime(df["date"])

    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    sentiments = df["sentiment"].tolist()
    prices = df["close_price"].tolist()
    actual_returns = df["return"].tolist()
    predicted_returns = df["predicted_return"].tolist()

    return render_template(
        "analyze.html",
        dates=dates,
        sentiments=sentiments,
        prices=prices,
        actual_returns=actual_returns,
        predicted_returns=predicted_returns,
        r2=results["r2"],
        mse=results["mse"],
        directional_accuracy=results["directional_accuracy"],
    )
