from typing import Tuple

from transformers import pipeline

_hf = pipeline("sentiment-analysis", truncation=True, max_length=512)


def analyze_sentiment(text: str) -> Tuple[str, float]:
    out = _hf(text[:1000])[0]
    return out["label"], out["score"]
