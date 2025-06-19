# scripts/bench_scraper.py
"""
Benchmark and validate the `fetch_articles` scraper in isolation.
"""
import os
import sys
import time

from dotenv import load_dotenv

# Ensure project root on path to import app modules
top = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, top)

# Load environment variables from project .env
env_path = os.path.join(top, ".env")
load_dotenv(env_path)

from app.agents.scraper import fetch_articles  # noqa: E402


def main():
    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        raise RuntimeError("GUARDIAN_API_KEY not set in .env")

    query = "Nvidia"
    page_size = 5
    start = time.perf_counter()
    articles = fetch_articles(query, api_key, page_size)
    duration = time.perf_counter() - start

    print(f"Fetched {len(articles)} articles in {duration:.2f}s")
    for art in articles:
        print(f"• {art['webTitle'][:60]}… ({art['publishDate']}) - {art['webUrl']}")


if __name__ == "__main__":
    main()
