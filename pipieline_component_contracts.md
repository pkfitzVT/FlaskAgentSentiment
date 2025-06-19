# MVP Pipeline Component Contracts

## 1. Scraper (`app.agents.scraper.fetch_articles`)

- **Inputs**  
  - `query: str` — e.g. `"Nvidia"`  
  - `api_key: str` — your Guardian API key  
  - `page_size: int` — number of articles to request  

- **Outputs**  
  - `List[dict]` — raw Guardian article objects, each containing:  
    ```yaml
    webTitle: str
    webUrl:   str
    webPublicationDate: str  # ISO timestamp, e.g. "2025-06-09T17:16:01Z"
    fields:
      bodyText: str
    # …plus other metadata…
    ```

- **Side-effects**  
  - HTTP GET to Guardian API  
  - Raises on non-200 responses

---

## 2. Sentiment (`app.agents.sentiment.analyze_sentiment`)

- **Inputs**  
  - `text: str` — up to the first 1,000 characters of article body

- **Outputs**  
  - `(label: str, score: float)`  
    - `label`: model’s class (e.g. `"POSITIVE"` / `"NEGATIVE"`)  
    - `score`: confidence (0.0–1.0)

- **Side-effects**  
  - Loads Hugging Face pipeline on first call  
  - No external writes

---

## 3. LLM Recommender (`app.agents.llm_recommender.recommend`)

- **Inputs**  
  - `title: str` — article headline  
  - `text: str` — up to the first 2,000 characters of body  
  - `score: float` — sentiment score from HF

- **Outputs**  
  - `ArticleRecc` (Pydantic model) with fields:  
    ```yaml
    title: str
    sentiment_score: float
    recommendation: one of [strong_sell, sell, hold, buy, strong_buy]
    rationale: str
    ```

- **Side-effects**  
  - Calls OpenAI ChatCompletion API  
  - Raises on JSON validation errors

---

## 4. Stock Prices (`app.agents.stock_prices.fetch_and_store_stock`)

- **Inputs**  
  - `session`: SQLAlchemy `Session`  
  - `symbol: str` — e.g. `"NVDA"`  
  - `dt: date` — article’s publication date

- **Outputs**  
  - `StockPrice` ORM instance with attributes:  
    ```yaml
    price_date: date
    open_price: Decimal
    high_price: Decimal
    low_price:  Decimal
    close_price: Decimal
    volume:      int
    ```
  - Or `None` if no data

- **Side-effects**  
  - Upserts into `stock_prices` table

---

## 5. DB Writer: Articles (`app.agents.db_writer.upsert_article`)

- **Inputs**  
  - `session`: SQLAlchemy `Session`  
  - `url: str`, `title: str`, `body: str`, `publish_date: date`

- **Outputs**  
  - `Article` ORM instance with attributes:  
    ```yaml
    article_id: int
    url, title, body_text, publish_date, fetched_at
    ```

- **Side-effects**  
  - INSERT or UPDATE in `articles` table

---

## 6. DB Writer: Analysis (`app.agents.db_writer.insert_analysis`)

- **Inputs**  
  - `session`: SQLAlchemy `Session`  
  - `article_id: int`, `sentiment_label: str`, `sentiment_score: float`,  
    `recommendation: str`, `rationale: str`, `price_date: date | None`

- **Outputs**  
  - `Analysis` ORM instance with attributes:  
    ```yaml
    analysis_id, article_id, sentiment_label, sentiment_score,
    recommendation, rationale, analysis_date, price_date
    ```

- **Side-effects**  
  - INSERT in `analysis` table

---

## Orchestrator Data Flow

1. **Fetch articles**  
   ```python
   arts = fetch_articles("Nvidia", GUARDIAN_KEY, 5)
