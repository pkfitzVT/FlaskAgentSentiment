# isort: skip_file

import datetime

import pytest
from sqlalchemy import inspect

from app.agents.db_writer import (
    get_session,
    insert_analysis,
    upsert_article,
    upsert_stock_price,
)


@pytest.fixture
def session():
    # in-memory SQLite for fast tests
    return get_session(db_url="sqlite:///:memory:")


def test_get_session_and_tables_created(session):
    inspector = inspect(session.get_bind())
    tables = set(inspector.get_table_names())
    assert {"articles", "analysis", "stock_prices"}.issubset(tables)


def test_upsert_article_insert_and_update(session):
    url = "http://example.com"
    # first insert
    art1 = upsert_article(
        session,
        url,
        "Title v1",
        "Body v1",
        datetime.date(2025, 1, 1),
    )
    assert art1.url == url
    assert art1.title == "Title v1"
    assert art1.body_text == "Body v1"
    assert art1.publish_date == datetime.date(2025, 1, 1)

    # then update
    art2 = upsert_article(
        session,
        url,
        "Title v2",
        "Body v2",
        datetime.date(2025, 2, 2),
    )
    assert art2.article_id == art1.article_id
    assert art2.title == "Title v2"
    assert art2.body_text == "Body v2"
    assert art2.publish_date == datetime.date(2025, 2, 2)


def test_insert_analysis(session):
    art = upsert_article(
        session,
        "http://x",
        "T",
        "B",
        datetime.date(2025, 3, 3),
    )
    ana = insert_analysis(
        session,
        art.article_id,
        "POS",
        0.9,
        "BUY",
        "rationale",
        price_date=datetime.date(2025, 3, 4),
    )
    assert ana.article_id == art.article_id
    assert ana.sentiment_label == "POS"
    assert pytest.approx(ana.sentiment_score) == 0.9
    assert ana.recommendation == "BUY"
    assert ana.rationale == "rationale"
    assert ana.price_date == datetime.date(2025, 3, 4)


def test_upsert_stock_price_insert_and_update(session):
    dt = datetime.date(2025, 4, 4)
    sp1 = upsert_stock_price(
        session,
        dt,
        10.0,
        12.0,
        12.5,
        9.5,
        100000,
    )
    assert sp1.price_date == dt
    assert float(sp1.open_price) == 10.0
    assert float(sp1.close_price) == 12.0
    assert float(sp1.high_price) == 12.5
    assert float(sp1.low_price) == 9.5
    assert sp1.volume == 100000

    # update same date
    sp2 = upsert_stock_price(
        session,
        dt,
        11.0,
        13.0,
        13.5,
        10.5,
        200000,
    )
    assert sp2.price_date == dt
    assert float(sp2.open_price) == 11.0
    assert float(sp2.close_price) == 13.0
    assert sp2.volume == 200000
