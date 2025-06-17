# tests/test_scraper.py

from app.agents.scraper import fetch_page


def test_fetch_page_returns_string():
    # “example.com” is just a placeholder
    result = fetch_page("https://example.com")
    assert isinstance(result, str), "Expected fetched page to be returned as a string"
