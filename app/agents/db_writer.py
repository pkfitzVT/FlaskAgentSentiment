# cspell:disable
import os

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Declarative base for ORM models
Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"  # noqa: cspell
    article_id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    body_text = Column(Text, nullable=False)
    publish_date = Column(Date, nullable=False)
    fetched_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    analyses = relationship("Analysis", back_populates="article")


class Analysis(Base):
    __tablename__ = "analysis"  # noqa: cspell
    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(
        Integer, ForeignKey("articles.article_id", ondelete="CASCADE"), nullable=False
    )
    sentiment_label = Column(String(32))
    sentiment_score = Column(Float, nullable=False)
    recommendation = Column(String(16), nullable=False)
    rationale = Column(Text)
    analysis_date = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    price_date = Column(Date)

    article = relationship("Article", back_populates="analyses")


class StockPrice(Base):
    __tablename__ = "stock_prices"  # noqa: cspell
    price_date = Column(Date, primary_key=True)
    open_price = Column(Numeric(12, 4))
    close_price = Column(Numeric(12, 4))
    high_price = Column(Numeric(12, 4))
    low_price = Column(Numeric(12, 4))
    volume = Column(BigInteger)


def get_session(db_url: str = None):
    """
    Create a SQLAlchemy session.
    Reads DATABASE_URL from the environment if db_url is not provided.
    """
    db_url = db_url or os.getenv("DATABASE_URL")
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def upsert_article(session, url: str, title: str, body: str, publish_date):
    """
    Insert or update an article record based on its URL.
    """
    stmt = (
        insert(Article)
        .values(url=url, title=title, body_text=body, publish_date=publish_date)
        .on_conflict_do_update(
            index_elements=["url"],
            set_={
                "title": title,
                "body_text": body,
                "publish_date": publish_date,
                "fetched_at": func.now(),
            },
        )
    )
    session.execute(stmt)
    session.commit()
    return session.query(Article).filter_by(url=url).one()


def insert_analysis(
    session,
    article_id: int,
    sentiment_label: str,
    sentiment_score: float,
    recommendation: str,
    rationale: str,
    price_date=None,
):
    """
    Add a new analysis record for a given article.
    """
    ana = Analysis(
        article_id=article_id,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        recommendation=recommendation,
        rationale=rationale,
        price_date=price_date,
    )
    session.add(ana)
    session.commit()
    return ana


def upsert_stock_price(session, price_date, open_p, close_p, high_p, low_p, volume):
    """
    Insert or update a stock price record for a trading day.
    """
    stmt = (
        insert(StockPrice)
        .values(
            price_date=price_date,
            open_price=open_p,
            close_price=close_p,
            high_price=high_p,
            low_price=low_p,
            volume=volume,
        )
        .on_conflict_do_update(
            index_elements=["price_date"],
            set_={
                "open_price": open_p,
                "close_price": close_p,
                "high_price": high_p,
                "low_price": low_p,
                "volume": volume,
            },
        )
    )
    session.execute(stmt)
    session.commit()
    return session.query(StockPrice).get(price_date)
