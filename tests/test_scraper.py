# tests/test_scraper.py
import pytest
import requests

from app.agents.scraper import fetch_page


def test_fetch_page_returns_string():
    # “example.com” is just a placeholder
    result = fetch_page("https://example.com")
    assert isinstance(result, str), "Expected fetched page to be returned as a string"


def test_fetch_page_raises_http_error(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            raise requests.HTTPError("404 Not Found")

    monkeypatch.setattr("app.agents.scraper.requests.get", lambda url: FakeResp())

    with pytest.raises(requests.HTTPError):
        fetch_page("https://example.com/missing")


def test_fetch_page_raises_timeout(monkeypatch):
    # Simulate a network timeout
    def fake_get(url):
        raise requests.Timeout("connection timed out")

    monkeypatch.setattr("app.agents.scraper.requests.get", fake_get)

    with pytest.raises(requests.Timeout):
        fetch_page("https://example.com/slow")


def test_fetch_page_uses_timeout(monkeypatch):
    captured = {}

    def fake_get(url, **kwargs):
        # capture any kwargs passed
        captured["url"] = url
        captured["kwargs"] = kwargs

        class FakeResp:
            def raise_for_status(self):
                pass

            @property
            def text(self):
                return "<html></html>"

        return FakeResp()

    monkeypatch.setattr("app.agents.scraper.requests.get", fake_get)

    result = fetch_page("https://example.com")
    assert isinstance(result, str)

    # Now assert that fetch_page passed a timeout argument:
    assert (
        "timeout" in captured["kwargs"]
    ), "Expected fetch_page to call requests.get with a timeout"
    assert isinstance(
        captured["kwargs"]["timeout"], (int, float)
    ), "timeout should be a number"


def test_fetch_page_follows_redirect(monkeypatch):
    # Simulate a redirect response that *already* contains the final HTML
    class FakeResp:
        status_code = 200
        text = "<html>Real Content</html>"

        def raise_for_status(self):
            pass

    # Our fake_get only gets called once, because requests did its own redirect
    def fake_get(url, **kwargs):
        return FakeResp()

    monkeypatch.setattr("app.agents.scraper.requests.get", fake_get)

    html = fetch_page("https://example.com/start")
    assert "Real Content" in html
