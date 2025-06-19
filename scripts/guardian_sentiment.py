#!/usr/bin/env python3
"""
Fetches Guardian articles on Nvidia, runs sentiment, and generates recommendations.
"""
import os
import re
import sys
from enum import Enum

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from transformers import pipeline

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class Recommendation(str, Enum):
    STRONG_SELL = "strong_sell"
    SELL = "sell"
    HOLD = "hold"
    BUY = "buy"
    STRONG_BUY = "strong_buy"


class ArticleRecc(BaseModel):
    title: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    recommendation: Recommendation
    rationale: str


# Load API keys
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GUARDIAN_KEY = os.getenv("GUARDIAN_API_KEY")
if not OPENAI_KEY or not GUARDIAN_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY and GUARDIAN_API_KEY in your .env")

# Instantiate clients
client = OpenAI(api_key=OPENAI_KEY)
hf = pipeline("sentiment-analysis", truncation=True, max_length=512)

SEARCH_URL = "https://content.guardianapis.com/search"
params = {
    "api-key": GUARDIAN_KEY,
    "q": "Nvidia",
    "show-fields": "bodyText",
    "page-size": 5,
    "order-by": "newest",
}


def clean_json_response(text: str) -> str:
    fence_re = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
    m = fence_re.search(text)
    return m.group(1) if m else text.strip()


def recommend_with_chatgpt(title: str, text: str, score: float) -> ArticleRecc:
    prompt = (
        "You are a financial analyst. Given an article headline, its sentiment score "
        "(-1 to +1), and the full article text, choose one of "
        "[strong_sell, sell, hold, buy, strong_buy] and justify in one sentence.\n"
        "Return exactly a JSON object with fields: title, sentiment_score, "
        "recommendation, rationale.\n\n"
        f"Headline: {title}\n"
        f"Sentiment score: {score:.2f}\n"
        "Text:" + "\n" + text
    )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert financial analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    raw = resp.choices[0].message.content
    json_str = clean_json_response(raw)
    try:
        return ArticleRecc.model_validate_json(json_str)
    except ValidationError:
        print("❌ Failed to validate JSON from LLM:\n", json_str)
        raise


def main():
    r = requests.get(SEARCH_URL, params=params, timeout=5)
    r.raise_for_status()
    arts = r.json()["response"]["results"]

    print(f"Found {len(arts)} Guardian articles for 'Nvidia'\n")
    for i, art in enumerate(arts, start=1):
        title = art.get("webTitle")
        url = art.get("webUrl")
        body_text = art.get("fields", {}).get("bodyText", "").strip()

        print(f"=== {i}. {title}\nURL: {url}\n")
        if not body_text:
            print("⚠️  No bodyText available; skipping.\n")
            continue

        hf_out = hf(body_text[:1000])[0]
        print(f"Sentiment: {hf_out['label']} " f"({hf_out['score']:.3f})\n")

        recc = recommend_with_chatgpt(title, body_text[:2000], hf_out["score"])
        print(f"Recommendation: {recc.recommendation.value}")
        print(f"Rationale:      {recc.rationale}\n")
        print("-" * 80)


if __name__ == "__main__":
    main()
