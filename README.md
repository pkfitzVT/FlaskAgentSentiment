# NVIDIA Sentiment Analysis Project Plan

## Project Skeleton (Agent-Oriented Scaffold)

```
project/
├── venv/                     # (optional) Python virtual environment
├── app/                      # Main application package
│   ├── __init__.py
│   ├── server.py             # Flask routes invoking orchestrator
│   ├── orchestrator.py       # Coordinates agent workflows (e.g. Prefect, LangChain)
│   ├── agents/               # Autonomous AI agents
│   │   ├── __init__.py
│   │   ├── scraper_agent.py      # Fetch & persist articles
│   │   ├── filter_agent.py       # Pre-filter neutrals using HF
│   │   ├── analyzer_agent.py     # Deep-dive LLM analysis, BUY/HOLD/SELL
│   │   ├── db_agent.py           # Read/write to PostgreSQL
│   │   └── dashboard_agent.py    # Prepare data for visualization
│   ├── models/               # Database models & migrations
│   │   ├── __init__.py
│   │   └── articles.py       # SQLAlchemy models
│   ├── sentiment/            # Legacy sentiment wrapper (optional)
│   │   ├── __init__.py
│   │   └── analyzer.py       # Wrap emotion_detector if still used
│   ├── templates/            # Flask/Jinja HTML templates
│   │   ├── index.html
│   │   └── dashboard.html    # Dashboard view
│   └── static/               # Static assets (JS, CSS)
│       └── mywebscript.js
├── tests/                    # PyTest tests for agents and API
│   ├── test_scraper.py
│   ├── test_filter.py
│   ├── test_analyzer.py
│   └── test_server.py
├── migrations/               # DB migration scripts (Alembic)
├── requirements.txt
├── requirements_dev.txt      # Dev dependencies: pytest, black, flake8, pylint
├── run.py                    # Simplified entry-point: imports and runs Flask app
└── README.md
```

---

## .gitignore

Create a `.gitignore` file at the project root with the following content to keep your repository clean:

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Virtual environment
venv/
.env

# Distribution / packaging
.build/
dist/
build/
*.egg-info/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.coverage
.coverage.*
.pytest_cache/

# PyCharm
.idea/
*.iml

# VSCode
.vscode/

# Logs and databases
*.log
*.sqlite3

# Jupyter Notebook checkpoints
.ipynb_checkpoints/
```

## Dependencies

Before you implement any agents, install and pin your project dependencies:

**Install core dependencies:**

```bash
pip install flask requests python-dotenv sqlalchemy psycopg2-binary alembic beautifulsoup4
```

**Install sentiment libraries:**

```bash
pip install transformers torch
```

**Install dev tools:**

```bash
pip install pytest pytest-cov black isort flake8 pylint
```

**Generate requirements files:**

```bash
pip freeze > requirements.txt
# On Windows PowerShell, use Select-String instead of grep:
pip freeze | Select-String -Pattern "pytest|black|isort|flake8|pylint" > requirements_dev.txt
```

## GitHub Issues & Timeline

| #  | Issue Title                      | Deliverable                                               | Due               |
| -- | -------------------------------- | --------------------------------------------------------- | ----------------- |
| 1  | Project Skeleton & PyCharm Setup | Initialize repo, add .gitignore, README, requirements.txt | Today 2 PM        |
| 2  | Set Up Venv & Dependencies       | Create venv, install Flask/requests/dotenv/pytest         | Today 3 PM        |
| 3  | Scraper Module                   | Implement `news_scraper.py` to fetch 5 NVIDIA articles    | Today 5 PM        |
| 4  | DB Models & Migrations           | Define SQLAlchemy models & Alembic migrations             | Today 6 PM        |
| 5  | Sentiment Analyzer Integration   | Write `analyzer.py` wrapping emotion\_detector            | Today 8 PM        |
| 6  | Flask API Endpoints              | Add `/scrape`, `/articles`, `/sentiment/daily` routes     | Tomorrow 9 AM     |
| 7  | Dashboard Frontend               | Basic Chart.js/table in `dashboard.html`                  | Tomorrow 10 AM    |
| 8  | Unit & Integration Tests         | Add pytest tests, aim for 90%+ coverage                   | Tomorrow 11 AM    |
| 9  | Static Analysis & Linting        | Black / Flask / isort; pylint 10/10                       | Tomorrow 11:30 AM |
| 10 | Demo & Documentation             | Update README, sample run instructions                    | Tomorrow 12 PM    |

---

## API Specification

| Endpoint           | Method | Request Parameters             | Response                                                  |
| ------------------ | ------ | ------------------------------ | --------------------------------------------------------- |
| `/`                | GET    | None                           | Renders `index.html`                                      |
| `/scrape`          | POST   | None                           | JSON: `{ "scraped": 5, "source": "Reuters RSS" }`         |
| `/articles`        | GET    | None                           | JSON list of articles: `[ {id, title, url, scraped_at} ]` |
| `/sentiment/daily` | GET    | `date` (optional, YYYY-MM-DD)  | JSON: `{ day, avg_joy, avg_anger, ..., dominant }`        |
| `/emotionDetector` | GET    | `textToAnalyze` (query string) | Plain text: formatted result or invalid message           |
| `/emotionDetector` | POST   | `text` (form data or JSON)     | Plain text: formatted result or invalid message           |

---

## Git Commit Plan & History Outline

Below is a proposed sequence of feature branches with commit messages, and a final merge history into `main`:

| Branch | Commit Message |   |   |   |
| ------ | -------------- | - | - | - |
|        |                |   |   |   |

|   |
| - |

|   |
| - |

| **feat/test-homepage**         | chore(tests): add test for homepage loading                        |   |   |   |
| ------------------------------ | ------------------------------------------------------------------ | - | - | - |
| **feat/homepage-endpoint**     | feat(server): implement `/` route rendering `index.html`           |   |   |   |
| **feat/test-emotion-endpoint** | chore(tests): add test for `/emotionDetector` blank-input handling |   |   |   |
| **feat/emotion-validation**    | feat(server): handle blank input with invalid-message response     |   |   |   |
| **feat/test-emotion-success**  | chore(tests): add test for valid emotion detection formatting      |   |   |   |
| **feat/emotion-success**       | feat(server): return formatted emotion scores and dominant emotion |   |   |   |
| **feat/test-scraper**          | chore(tests): add test for NVIDIA RSS scraper                      |   |   |   |
| **feat/scraper-module**        | feat(scraper): implement RSS scraping & article persistence        |   |   |   |
| **feat/test-analyzer**         | chore(tests): add test for sentiment analyzer integration          |   |   |   |
| **feat/analyzer-module**       | feat(analyzer): integrate emotion\_detector into analyzer module   |   |   |   |
| **chore/ci-config**            | chore(ci): add pytest/flake8/black pipeline to GitHub Actions      |   |   |   |
| **chore/pylint-10**            | chore(lint): update code to achieve 10/10 pylint score             |   |   |   |

### Example Merge History on `main`

```
* Merge pull request #12 from chore/pylint-10          # chore(lint): 10/10 pylint score
* Merge pull request #11 from chore/ci-config          # chore(ci): CI pipeline setup
* Merge pull request #10 from feat/analyzer-module     # feat(analyzer): emotion analyzer integration
* Merge pull request #9  from feat/test-analyzer       # chore(tests): test analyzer
* Merge pull request #8  from feat/scraper-module      # feat(scraper): NVIDIA RSS scraper
* Merge pull request #7  from feat/test-scraper        # chore(tests): test scraper
* Merge pull request #6  from feat/emotion-success     # feat(server): emotion endpoint success
* Merge pull request #5  from feat/test-emotion-success# chore(tests): test valid emotion
* Merge pull request #4  from feat/emotion-validation  # feat(server): blank-input validation
* Merge pull request #3  from feat/test-emotion-endpoint# chore(tests): test emotion endpoint
* Merge pull request #2  from feat/homepage-endpoint   # feat(server): homepage endpoint
* Merge pull request #1  from feat/test-homepage       # chore(tests): test homepage
```

## Tech Stack Breakdown

To implement this NVIDIA sentiment analysis pipeline, here’s the recommended technology stack and libraries by component:

| Component                | Technology / Library                            | Purpose                                                   |
| ------------------------ | ----------------------------------------------- | --------------------------------------------------------- |
| **Web Framework**        | Flask                                           | Lightweight API & server routing                          |
| **Environment**          | python-dotenv                                   | Load `.env` configuration                                 |
| **Scraping**             | requests, BeautifulSoup                         | HTTP requests & HTML parsing for RSS/website scraping     |
| **Database**             | PostgreSQL + SQLAlchemy + Alembic/Flask‑Migrate | Relational storage, ORM mapping, migrations               |
| **Sentiment Analysis**   | IBM Watson NLU SDK / Hugging‑Face Transformers  | Emotion detection; HF if you need open‑source replacement |
| **Dashboard**            | Chart.js (in templates) or Plotly Dash          | Visualize sentiment scores and trends                     |
| **Testing**              | pytest, pytest‑cov                              | Unit & integration tests, coverage reporting              |
| **Linting & Formatting** | black, isort, flake8, pylint                    | Code style, import sorting, static analysis               |
| **CI/CD**                | GitHub Actions                                  | Automated test & lint pipelines                           |

## Module Pseudocode

Below is high-level pseudocode for each key module:

### 1. `scraper/news_scraper.py`

```
function fetch_latest_articles():
    sources = ["https://www.reuters.com/rss/technologyNews"]
    articles = []
    for source in sources:
        rss = http_get(source)
        items = parse_rss(rss)
        for item in items[:5]:  # limit to 5
            title, url = extract_title_url(item)
            content = fetch_article_content(url)
            articles.append({"title": title, "url": url, "content": content})
    return articles

function save_articles_to_db(articles):
    for article in articles:
        if not exists_in_db(article.url):
            db.insert("articles", article)
```

### 2. `models/articles.py`

```
class Article(Base):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    url = Column(Text, unique=True)
    content = Column(Text)
    scraped_at = Column(DateTime, default=now)

class ArticleSentiment(Base):
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("article.id"))
    anger = Column(Float)
    disgust = Column(Float)
    fear = Column(Float)
    joy = Column(Float)
    sadness = Column(Float)
    dominant = Column(Text)
    scored_at = Column(DateTime, default=now)

class DailySentiment(Base):
    day = Column(Date, primary_key=True)
    avg_anger = Column(Float)
    ...
    dominant = Column(Text)
```

### 3. `sentiment/analyzer.py`

```
function analyze_new_articles():
    articles = db.query("articles").filter(no_sentiment_today)
    for a in articles:
        scores = emotion_detector(a.content)
        db.insert("article_sentiment", {"article_id": a.id, **scores})
```

### 4. `app/server.py`

```
route GET /:
    return render_template("index.html")

route GET or POST /emotionDetector:
    text = extract_text_from_request()
    scores = emotion_detector(text)
    if scores.dominant_emotion is None:
        return "Invalid text! Please try again!"
    return format_response(scores)

route POST /scrape:
    articles = fetch_latest_articles()
    save_articles_to_db(articles)
    return json_response({"scraped": len(articles)})

route GET /articles:
    list = db.query("articles").all()
    return json_response(list)

route GET /sentiment/daily:
    day = get_query_param("date", today)
    stats = db.query("daily_sentiment").filter(day)
    return json_response(stats)
```

## Agent-Oriented Extension

To adapt to an AI Agent Developer approach, we can refactor modules into autonomous agents and introduce an orchestrator:

```
project/
├── app/
│   ├── __init__.py
│   ├── orchestrator.py       # Coordinates agent workflows using Prefect or LangChain
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scraper_agent.py      # Fetch & persist articles
│   │   ├── filter_agent.py       # Pre-filter neutrals using HF
│   │   ├── analyzer_agent.py     # Deep-dive LLM analysis, BUY/HOLD/SELL
│   │   ├── db_agent.py           # Read/write to PostgreSQL
│   │   └── dashboard_agent.py    # Prepare data for visualization
│   └── server.py                 # Flask API routes invoking the orchestrator
└── ...                            # rest of project
```

### Orchestrator Pseudocode (`orchestrator.py`)

```
def run_pipeline():
    articles = scraper_agent.fetch()
    filtered = filter_agent.keep_non_neutral(articles)
    signals = analyzer_agent.evaluate(filtered)
    db_agent.store_signals(signals)
    dashboard_agent.update()
```

### Benefits of Agents

- **Modularity:** Each agent can be developed, tested, and deployed independently.
- **Scalability:** Agents can be scaled up/down (e.g., LLM agent on GPU nodes).
- **Observability:** Orchestrator logs each agent’s status for monitoring and retries.

## Building the Scraper Agent

Below are the step-by-step instructions to build the **Scraper Agent**, from setting up the directory structure to creating a Working MVP and validating its functionality.

### 1. Directory Structure

Place the scraper agent under the `app/agents/` folder:

```
project/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── scraper_agent.py
│   └── server.py
```

### 2. MVP Implementation

In `app/agents/scraper_agent.py`, define a class with a simple `fetch()` method:

```python
# app/agents/scraper_agent.py
import requests
from bs4 import BeautifulSoup

class ScraperAgent:
    """
    Agent responsible for fetching and parsing the latest NVIDIA articles.
    """
    def __init__(self, feeds, db_agent):
        self.feeds = feeds          # List of RSS or API endpoints
        self.db = db_agent          # Dependency for saving to DB

    def fetch(self):
        """
        Fetch up to 5 articles from each feed, dedupe by URL,
        save new ones via db_agent, and return list of article data.
        """
        new_articles = []
        for feed_url in self.feeds:
            resp = requests.get(feed_url, timeout=5)
            resp.raise_for_status()
            items = BeautifulSoup(resp.text, "xml").find_all("item")[:5]
            for item in items:
                url = item.link.text
                title = item.title.text
                content = self._fetch_content(url)
                if not self.db.exists(url):
                    self.db.save_article({
                        'title': title,
                        'url': url,
                        'content': content
                    })
                    new_articles.append(url)
        return new_articles

    def _fetch_content(self, article_url):
        resp = requests.get(article_url, timeout=5)
        return resp.text
```

### 3. Dependency Stub for Testing

Create a fake `db_agent` with `exists()` and `save_article()` methods to use in unit tests.

### 4. Unit Tests (PyTest)

In `tests/test_scraper.py`, write tests that:

1. **Mock** `requests.get` to return a sample RSS feed and HTML.
2. Initialize `ScraperAgent` with a list of test feeds and a stub `db_agent`.
3. Assert that `fetch()` returns the expected new URLs.
4. Assert that `db_agent.save_article()` was called only for unseen URLs.

```python
# tests/test_scraper.py
import pytest
from app.agents.scraper_agent import ScraperAgent

class DummyDB:
    def __init__(self): self.saved = []
    def exists(self, url): return False
    def save_article(self, article): self.saved.append(article)

@ pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    class DummyResp:
        text = "<rss><item><title>Test</title><link>http://a</link></item></rss>"
        def raise_for_status(self): pass
    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: DummyResp())
    yield

def test_scraper_fetch(monkeypatch):
    db = DummyDB()
    agent = ScraperAgent(['dummy_feed'], db)
    new = agent.fetch()
    assert new == ['http://a']
    assert len(db.saved) == 1
```

### 5. Manual Validation

1. Run the test suite: `pytest tests/test_scraper.py -q` (should pass).
2. In a Python shell:
   ```bash
   from app.agents.scraper_agent import ScraperAgent
   from app.agents.db_agent import DbAgent  # real implementation
   agent = ScraperAgent(['https://www.reuters.com/rss/technologyNews'], DbAgent())
   print(agent.fetch())  # should print list of new article URLs
   ```

### 6. Integrate with Orchestrator or Flask

Once validated, call `ScraperAgent.fetch()` from your orchestrator or within the `/scrape` Flask route to incorporate it into the full pipeline.

## How to Print / Export

To adapt to an AI Agent Developer approach, we can refactor modules into autonomous agents and introduce an orchestrator:

```
project/
├── app/
│   ├── __init__.py
│   ├── orchestrator.py       # Coordinates agent workflows using Prefect or LangChain
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scraper_agent.py      # Fetch & persist articles
│   │   ├── filter_agent.py       # Pre-filter neutrals using HF
│   │   ├── analyzer_agent.py     # Deep-dive LLM analysis, BUY/HOLD/SELL
│   │   ├── db_agent.py           # Read/write to PostgreSQL
│   │   └── dashboard_agent.py    # Prepare data for visualization
│   └── server.py                 # Flask API routes invoking the orchestrator
└── ...                            # rest of project
```

### Orchestrator Pseudocode (`orchestrator.py`)

```
def run_pipeline():
    articles = scraper_agent.fetch()
    filtered = filter_agent.keep_non_neutral(articles)
    signals = analyzer_agent.evaluate(filtered)
    db_agent.store_signals(signals)
    dashboard_agent.update()
```

### Benefits of Agents

- **Modularity:** Each agent can be developed, tested, and deployed independently.
- **Scalability:** Agents can be scaled up/down (e.g., LLM agent on GPU nodes).
- **Observability:** Orchestrator logs each agent’s status for monitoring and retries.

## How to Print / Export

- This document can be copied into a Markdown file (`PLAN.md`) in your repo.
- Clone or download the file, then print via a Markdown viewer or GitHub.

Good luck! Feel free to adjust any timelines or scope as needed.

