import os  # noqa: E402

os.environ["OPENAI_API_KEY"] = "dummy-key"

import pytest  # noqa: E402
from pydantic import ValidationError  # noqa: E402

from app.agents.llm_recommender import ArticleRecc, recommend  # noqa: E402


class DummyClient:
    """Simulates an OpenAI client returning a fixed JSON string."""

    def __init__(self, response_content: str):
        self.response_content = response_content

    def create(self, *args, **kwargs):
        class Choice:
            def __init__(self, content: str):
                self.message = type("M", (), {"content": content})

        return type("R", (), {"choices": [Choice(self.response_content)]})


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Monkeypatch the OpenAI client to use our DummyClient."""
    import app.agents.llm_recommender as mod

    dummy = DummyClient(
        '{"title":"T","sentiment_score":0.5,'
        '"recommendation":"hold","rationale":"Balanced."}'
    )
    # Replace the nested chat.completions.create
    client_stub = type("C", (), {"chat": type("D", (), {"completions": dummy})})
    monkeypatch.setattr(mod, "_client", client_stub)
    yield


def test_recommend_happy_path():
    """Test that recommend returns a valid ArticleRecc on good JSON."""
    rec = recommend("Headline", "Some text", 0.5)
    assert isinstance(rec, ArticleRecc)
    assert rec.title == "T"
    assert pytest.approx(rec.sentiment_score) == 0.5
    assert rec.recommendation.value == "hold"
    assert "Balanced" in rec.rationale


def test_recommend_invalid_json(monkeypatch):
    """Test that recommend raises ValidationError on malformed JSON."""
    import app.agents.llm_recommender as mod

    bad = DummyClient("not a json")
    client_stub = type("C", (), {"chat": type("D", (), {"completions": bad})})
    monkeypatch.setattr(mod, "_client", client_stub)

    with pytest.raises(ValidationError):
        recommend("X", "Y", 0.0)
