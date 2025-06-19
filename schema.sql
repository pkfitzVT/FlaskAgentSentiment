-- 1) Articles table
CREATE TABLE articles (
  article_id   SERIAL PRIMARY KEY,
  url          TEXT        UNIQUE     NOT NULL,
  title        TEXT                    NOT NULL,
  body_text    TEXT                    NOT NULL,
  publish_date DATE                    NOT NULL,
  fetched_at   TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2) Analysis table
CREATE TABLE analysis (
  analysis_id      SERIAL PRIMARY KEY,
  article_id       INTEGER REFERENCES articles(article_id) ON DELETE CASCADE,
  sentiment_label  VARCHAR(32),
  sentiment_score  REAL        NOT NULL,
  recommendation   VARCHAR(16) NOT NULL,
  rationale        TEXT,
  analysis_date    TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 3) Stock prices table
CREATE TABLE stock_prices (
  price_date   DATE         PRIMARY KEY,
  open_price   NUMERIC(12,4),
  close_price  NUMERIC(12,4),
  high_price   NUMERIC(12,4),
  low_price    NUMERIC(12,4),
  volume       BIGINT
);

-- 4) Link analysis to stock_prices
ALTER TABLE analysis
  ADD COLUMN price_date DATE
    REFERENCES stock_prices(price_date);

-- 5) Indexes for performance
CREATE INDEX idx_articles_publish_date ON articles(publish_date);
CREATE INDEX idx_analysis_article   ON analysis(article_id);
CREATE INDEX idx_analysis_price_date ON analysis(price_date);
