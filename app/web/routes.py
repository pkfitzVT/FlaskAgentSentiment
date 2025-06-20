# app/web/routes.py
from flask import Blueprint, abort, render_template

from app.agents.db_writer import Analysis, Article, StockPrice, get_session

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
    session = get_session()
    # Get publish_date, sentiment_score, and a price for each article
    # (Modify join logic to match your actual DB structure)
    results = (
        session.query(
            Article.publish_date,
            Analysis.sentiment_score,
            Analysis.recommendation,
            StockPrice.close_price,
        )
        .join(Analysis, Article.article_id == Analysis.article_id)
        .join(StockPrice, StockPrice.price_date == Article.publish_date)
        .order_by(Article.publish_date)
        .all()
    )
    # Unpack columns for plotting
    dates = [r[0].isoformat() for r in results]
    sentiments = [r[1] for r in results]
    recs = [r[2] for r in results]
    prices = [float(r[3]) for r in results]

    # Pass the data as dict to the template
    return render_template(
        "analyze.html",
        dates=dates,
        sentiments=sentiments,
        prices=prices,
        recs=recs,
    )
