import requests


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text
