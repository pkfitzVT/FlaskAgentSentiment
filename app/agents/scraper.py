import logging
from datetime import datetime
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)
GUARDIAN_URL = "https://content.guardianapis.com/search"


def fetch_articles(query: str, api_key: str, page_size: int = 5) -> List[Dict]:
    """
    Fetches and parses Guardian articles matching `query`.

    Returns a list of dicts with keys:
      - webUrl: str
      - webTitle: str
      - bodyText: str
      - publishDate: datetime.date

    Filters out any entries missing required fields or malformed dates.
    """
    params = {
        "api-key": api_key,
        "q": query,
        "show-fields": "bodyText",
        "page-size": page_size,
        "order-by": "newest",
    }
    try:
        r = requests.get(GUARDIAN_URL, params=params, timeout=5)
        r.raise_for_status()
        payload = r.json()
        results = payload.get("response", {}).get("results", [])
    except requests.RequestException as e:
        logger.error("Guardian API request failed: %s", e)
        return []
    except ValueError as e:
        logger.error("Failed to parse JSON from Guardian: %s", e)
        return []

    articles: List[Dict] = []
    for art in results:
        url = art.get("webUrl")
        title = art.get("webTitle")
        body = art.get("fields", {}).get("bodyText", "").strip()
        iso_dt = art.get("webPublicationDate")

        # Validate fields
        if not url or not title or not body or not iso_dt:
            logger.warning("Skipping article missing data: %s", art)
            continue

        # Parse ISO date with trailing Z support
        try:
            dt_str = iso_dt.rstrip("Z") + "+00:00" if iso_dt.endswith("Z") else iso_dt
            pub_date = datetime.fromisoformat(dt_str).date()
        except Exception as e:
            logger.warning(
                "Invalid publication date '%s' for URL %s: %s", iso_dt, url, e
            )
            continue

        articles.append(
            {
                "webUrl": url,
                "webTitle": title,
                "bodyText": body,
                "publishDate": pub_date,
            }
        )

    return articles
