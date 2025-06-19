# app/sentiment.py


def analyze_sentiment(text: str) -> dict:
    """
    Stub sentiment analyzer. Replace with real model or API call.
    For now, just returns text length and a dummy score.
    """
    words = text.split()
    return {"word_count": len(words), "score": 0.0, "label": "neutral"}  # dummy
