
# FlaskAgentSentiment

End‑to‑end pipeline that scrapes Guardian articles about NVIDIA, analyzes sentiment
with HuggingFace, gets a buy/sell/hold recommendation from OpenAI, and stores
everything in PostgreSQL.

---

## Directory Structure

```
FlaskAgentSentiment/
├── app/
│   ├── __init__.py
│   ├── orchestrator.py
│   └── agents/
│       ├── scraper.py
│       ├── sentiment.py
│       ├── llm_recommender.py
│       ├── stock_prices.py
│       └── db_writer.py
├── tests/                ← pytest unit‑tests for every agent
├── .pre‑commit‑config.yaml
└── pyproject.toml        ← black & isort use profile=black
```

---

## Components

| Module (function) | Input | Output | Error Handling |
|-------------------|-------|--------|----------------|
| **scraper.py**<br>`fetch_articles(query, api_key, page_size)` | Guardian keyword, API key, page size | list\[dict\]: `webUrl`, `webTitle`, `bodyText`, `publishDate` | • `requests.RequestException` → returns empty list.<br>• `ValueError` on JSON parse → empty list.<br>Warn on missing fields. |
| **sentiment.py**<br>`analyze_sentiment(text)` | text ≤1 000 chars | tuple `(label:str, score:float)` | Any HF pipeline exception bubbles up (caller decides). |
| **llm_recommender.py**<br>`recommend(title, text, score)` | headline, full text, sentiment score | `ArticleRecc` Pydantic model | • `OpenAIError` → `APIRecommendationError`.<br>• ValidationError on malformed JSON bubbles up. |
| **db_writer.py** | SQLAlchemy ORM helpers | Article, Analysis, StockPrice rows | • Uses `ON CONFLICT` for idempotent upserts.<br>• Any `DatabaseError` bubbles. |
| **stock_prices.py**<br>`fetch_and_store_stock(session, symbol, dt)` | SQLAlchemy session, ticker, date | `StockPrice` ORM obj | • Raises `KeyError` if yfinance columns missing.<br>• Returns `None` if no daily data. |
| **orchestrator.py**<br>`orchestrate_nvidia(batch_size=50)` | batch_size from CLI | None (writes DB) | • Skips article if its analysis exists **today**.<br>• Logs and continues on sentiment/LLM/db failure. |

---

## PostgreSQL Schema

### `articles`

| column | type | notes |
|--------|------|-------|
| article_id | serial PK |
| url | text unique |
| title | text |
| body_text | text |
| publish_date | date |
| fetched_at | timestamptz default now() |

### `analysis`

| column | type | notes |
|--------|------|-------|
| analysis_id | serial PK |
| article_id | FK → `articles.article_id` |
| sentiment_label | varchar(32) |
| sentiment_score | float |
| recommendation | varchar(16) (`strong_sell` … `strong_buy`) |
| rationale | text |
| analysis_date | timestamptz default now() |

### `stock_prices`

| column | type |
|--------|------|
| price_date | date PK |
| open_price | numeric(12,4) |
| close_price | numeric(12,4) |
| high_price | numeric(12,4) |
| low_price | numeric(12,4) |
| volume | bigint |

---

## Orchestrator Flow

1. **Scrape** up to *N* Guardian articles (`batch_size`, default 50).
2. **Upsert** each URL into `articles`.
3. **Skip** URLs already with an `analysis_date = today`.
4. **Sentiment** → HuggingFace (pipeline error ⇒ neutral *0.0*).
5. **LLM** → OpenAI (error ⇒ hold / fallback).
6. **insert_analysis** → writes record.
7. Logs summary count.

Run:

```bash
python -m app.orchestrator -n 100   # fetch 100 articles
```

---

## Unit Tests

| File | What it covers |
|------|----------------|
| `tests/test_scraper.py` | mocks Guardian API, asserts 200 → 5 parsed dicts |
| `tests/test_sentiment.py` | mocks HF pipeline, asserts label+score |
| `tests/test_llm_recommender.py` | monkeypatches `_client`, tests happy & error paths |
| `tests/test_db_writer.py` | uses SQLite memory DB to upsert/select |
| `tests/test_orchestrator.py` | end‑to‑end with in‑memory DB + stubbed agents |

Run all tests:

```bash
pytest -q
```

---

## Pre‑commit Setup

```bash
pip install pre-commit
pre-commit install        # one‑time
pre-commit run --all-files
```

Config uses:

* **Black** (line‑length 88)  
* **isort** (`profile = black`)  
* **Flake8** (ignore E203,W503)  

—

Happy hacking! 🚀
