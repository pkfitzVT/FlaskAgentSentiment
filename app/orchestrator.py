# flake8: noqa: E402
#!/usr/bin/env python3
# app/orchestrator.py

from dotenv import load_dotenv

load_dotenv()  # loads GUARDIAN_API_KEY & OPENAI_API_KEY

import logging
import os
from datetime import date
from typing import Dict, List

from psycopg2 import DatabaseError
from pydantic import ValidationError
from requests import HTTPError
from sqlalchemy import Date, cast, select
from sqlalchemy.orm import Session

from app.agents.db_writer import Analysis, get_session, insert_analysis, upsert_article
from app.agents.llm_recommender import APIRecommendationError, recommend
from app.agents.scraper import fetch_articles
from app.agents.sentiment import analyze_sentiment

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("app.orchestrator")


def orchestrate_nvidia(batch_size: int = 50) -> None:
    """
    1) Scrape up to `batch_size` NVIDIA articles.
    2) Skip ones already analyzed today.
    3) Analyze & save every new article:
       - sentiment analysis
       - LLM recommendation
       - insert_analysis
    """
    guardian_key = os.getenv("GUARDIAN_API_KEY")
    if not guardian_key:
        logger.error("Missing GUARDIAN_API_KEY")
        return

    session: Session = get_session()
    today = date.today()

    # 1) Scrape articles
    try:
        raw = fetch_articles("nvidia", guardian_key, page_size=batch_size)
        logger.info("Scraped %d articles", len(raw))
    except HTTPError as e:
        logger.error("Scraper failed: %s", e)
        return

    # 2) Identify new articles
    new_items = []
    for art in raw:
        try:
            art_obj = upsert_article(
                session,
                url=art["webUrl"],
                title=art["webTitle"],
                body=art["bodyText"],
                publish_date=art["publishDate"],
            )
        except DatabaseError as e:
            logger.error("upsert_article failed for %s: %s", art["webUrl"], e)
            continue

        seen = session.execute(
            select(Analysis).where(
                Analysis.article_id == art_obj.article_id,
                cast(Analysis.analysis_date, Date) == today,
            )
        ).first()
        if seen:
            continue

        new_items.append((art, art_obj))

    if not new_items:
        logger.info("No new articles to analyze today.")
        return

    # 3) Process each new article
    for art, art_obj in new_items:
        title, body = art["webTitle"], art["bodyText"]

        # Sentiment analysis
        try:
            label, score = analyze_sentiment(body)
        except Exception as e:
            logger.warning("Sentiment analysis failed for %r: %s", title, e)
            label, score = "NEUTRAL", 0.0

        # LLM recommendation
        try:
            rec = recommend(title, body, score)
            rec_data = rec.model_dump(mode="json")
        except (APIRecommendationError, ValidationError) as e:
            logger.warning("LLM recommendation failed for %r: %s", title, e)
            rec_data = {
                "sentiment_score": score,
                "recommendation": "hold",
                "rationale": "fallback due to error",
            }

        # Insert analysis record
        try:
            insert_analysis(
                session,
                article_id=art_obj.article_id,
                sentiment_label=label,
                sentiment_score=score,
                recommendation=rec_data["recommendation"],
                rationale=rec_data["rationale"],
            )
            logger.info("Saved analysis for %r", title)
        except DatabaseError as e:
            logger.error(
                "insert_analysis failed for article_id %d: %s", art_obj.article_id, e
            )

    logger.info("Pipeline complete: processed %d new articles", len(new_items))


if __name__ == "__main__":
    orchestrate_nvidia()
