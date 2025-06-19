#!/usr/bin/env python3
# smoke_test_news_data.py

import os

import requests
from dotenv import load_dotenv

from app.agents.modules import fetch_page


def main():
    here = os.path.dirname(__file__)
    load_dotenv(os.path.join(here, ".env"))

    api_key = os.getenv("NYT_API_KEY")
    if not api_key:
        raise RuntimeError("NYT_API_KEY not set in .env or environment")

    # 1) Keyword search for Nvidia
    search_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {
        "q": "Nvidia",
        "api-key": api_key,
        "sort": "newest",
        "page": 0,
    }
    resp = requests.get(search_url, params=params, timeout=5)
    resp.raise_for_status()
    payload = resp.json()

    # DEBUG: show how many docs we got
    docs = payload.get("response", {}).get("docs") or []
    print(f">>> {len(docs)} document(s) returned.")

    if not docs:
        print("No ‘Nvidia’ articles found.")
        return

    # 2) Fetch & print article bodies
    for i, doc in enumerate(docs[:3], start=1):
        title = doc.get("headline", {}).get("main", "<no title>")
        url = doc.get("web_url")
        print(f"\n=== Article {i}: {title}\nURL: {url}\n")

        # 3) Download the full page
        html = fetch_page(url)

        # 4) Extract and print <article>…</article>
        start = html.find("<article")
        end = html.find("</article>") + len("</article>")
        snippet = html[start:end] if start != -1 and end != -1 else html[:500]
        print(snippet)
        print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
