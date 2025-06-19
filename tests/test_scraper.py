from datetime import date

import pytest
import requests

from app.agents.scraper import fetch_articles


class DummyResponse:
    def __init__(self, json_data, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise requests.HTTPError(f"Status {self.status_code}")

    def json(self) -> dict:
        return self._json


@pytest.fixture
def sample_payload() -> dict:
    return {
        "response": {
            "results": [
                {
                    "webUrl": "https://example.com/a",
                    "webTitle": "Test Title A",
                    "fields": {"bodyText": "Some body text A."},
                    "webPublicationDate": "2025-06-10T12:00:00Z",
                },
                {
                    "webUrl": "https://example.com/b",
                    "webTitle": "Test Title B",
                    "fields": {"bodyText": "Some body text B."},
                    "webPublicationDate": "2025-06-11T15:30:00Z",
                },
            ]
        }
    }


def test_fetch_articles_happy_path(monkeypatch, sample_payload):
    def fake_get(url: str, params: dict, timeout: float):
        assert "content.guardianapis.com" in url
        assert params["q"] == "Nvidia"
        return DummyResponse(sample_payload)

    monkeypatch.setattr("requests.get", fake_get)

    articles = fetch_articles("Nvidia", "dummy-key", page_size=2)
    assert len(articles) == 2

    first, second = articles
    assert first["webUrl"] == "https://example.com/a"
    assert first["webTitle"] == "Test Title A"
    assert first["bodyText"] == "Some body text A."
    assert isinstance(first["publishDate"], date)
    assert first["publishDate"].isoformat() == "2025-06-10"

    assert second["webUrl"].endswith("/b")
    assert second["publishDate"].day == 11


def test_fetch_articles_api_error(monkeypatch):
    def broken_get(*args, **kwargs):
        raise requests.ConnectionError("fail")

    monkeypatch.setattr("requests.get", broken_get)
    result = fetch_articles("Anything", "key", page_size=5)
    assert result == []


def test_fetch_articles_bad_json(monkeypatch):
    class BadResponse(DummyResponse):
        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: BadResponse({}))
    result = fetch_articles("X", "key", page_size=5)
    assert result == []
