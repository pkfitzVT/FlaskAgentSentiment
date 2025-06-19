# flake8: noqa: E402
import os

os.environ["OPENAI_API_KEY"] = "dummy-key"

import pytest
from openai import OpenAIError
from pydantic import ValidationError

from app.agents.llm_recommender import (APIRecommendationError, ArticleRecc,
                                        recommend)


class DummyCompletions:
    """Simulates the .chat.completions.create interface."""

    def __init__(self, content: str, error: Exception = None):
        self.content = content
        self.error = error

    def create(self, *args, **kwargs):
        if self.error:
            raise self.error

        class Choice:
            def __init__(self, content: str):
                self.message = type("M", (), {"content": content})

        return type("R", (), {"choices": [Choice(self.content)]})


class DummyClient:
    """Holds a DummyCompletions under .chat.completions."""

    def __init__(self, completions: DummyCompletions):
        self.chat = type("Chat", (), {"completions": completions})


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Monkey-patch llm_recommender._client to use DummyClient by default."""
    import app.agents.llm_recommender as mod

    good_json = (
        '{"title":"T","sentiment_score":0.5,'
        '"recommendation":"hold","rationale":"Balanced."}'
    )
    dummy = DummyClient(DummyCompletions(good_json))
    monkeypatch.setattr(mod, "_client", dummy)
    yield


def test_recommend_happy_path():
    rec = recommend("Headline", "Some text", 0.5)
    assert isinstance(rec, ArticleRecc)
    assert rec.title == "T"
    assert rec.sentiment_score == pytest.approx(0.5)
    assert rec.recommendation.value == "hold"
    assert "Balanced" in rec.rationale


def test_recommend_invalid_json(monkeypatch):
    import app.agents.llm_recommender as mod

    # Return invalid JSON string
    dummy = DummyClient(DummyCompletions("not-a-json"))
    monkeypatch.setattr(mod, "_client", dummy)

    with pytest.raises(ValidationError):
        recommend("X", "Y", 0.0)


def test_recommend_api_error(monkeypatch):
    import app.agents.llm_recommender as mod

    # Simulate API error
    dummy = DummyClient(DummyCompletions("", error=OpenAIError("API down")))
    monkeypatch.setattr(mod, "_client", dummy)

    with pytest.raises(APIRecommendationError):
        recommend("X", "Y", 0.0)
