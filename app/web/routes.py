# app/web/routes.py
from flask import Blueprint, abort, render_template

from app.agents.db_writer import Analysis, Article, get_session

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
