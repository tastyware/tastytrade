from datetime import date

from tastytrade.metrics import (
    a_get_dividends,
    a_get_earnings,
    a_get_market_metrics,
    a_get_risk_free_rate,
    get_dividends,
    get_earnings,
    get_market_metrics,
    get_risk_free_rate,
)


async def test_get_dividends_async(session):
    await a_get_dividends(session, "SPY")


async def test_get_earnings_async(session):
    await a_get_earnings(session, "AAPL", date.today())


async def test_get_market_metrics_async(session):
    await a_get_market_metrics(session, ["SPY", "AAPL"])


async def test_get_risk_free_rate_async(session):
    await a_get_risk_free_rate(session)


def test_get_dividends(session):
    get_dividends(session, "SPY")


def test_get_earnings(session):
    get_earnings(session, "AAPL", date.today())


def test_get_market_metrics(session):
    get_market_metrics(session, ["SPY", "AAPL"])


def test_get_risk_free_rate(session):
    get_risk_free_rate(session)
