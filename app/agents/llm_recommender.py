import os
import re
from enum import Enum

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError


def clean_json_response(text: str) -> str:
    """
    Strip markdown fences from around JSON response.
    """
    fence_re = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
    m = fence_re.search(text)
    return m.group(1) if m else text.strip()


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


# Instantiate OpenAI client
_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError("Please set OPENAI_API_KEY in your environment")
_client = OpenAI(api_key=_api_key)


def recommend(title: str, text: str, score: float) -> ArticleRecc:
    """
    Call ChatGPT to get a buy/sell/hold recommendation.
    """
    intro = (
        "You are a financial analyst. Given an article headline, its sentiment score"
        " (-1.0 to +1.0), and the full article text, choose one of the following"
    )
    choices = " [strong_sell, sell, hold, buy, strong_buy] and justify in one sentence."
    fields = (
        "Return exactly a JSON object with these fields: title, sentiment_score,"
        " recommendation, rationale."
    )
    prompt = (
        f"{intro}{choices} {fields}\n\n"
        f"Headline: {title}\n"
        f"Sentiment score: {score:.2f}\n"
        "Text: " + text
    )
    resp = _client.chat.completions.create(
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
    except ValidationError as e:
        print("❌ JSON validation error:", e)
        print("Raw JSON:", json_str)
        raise
