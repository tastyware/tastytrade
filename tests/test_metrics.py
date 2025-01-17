from datetime import date

from tastytrade import Session
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


async def test_get_dividends_async(session: Session):
    await a_get_dividends(session, "SPY")


async def test_get_earnings_async(session: Session):
    await a_get_earnings(session, "AAPL", date.today())


async def test_get_market_metrics_async(session: Session):
    await a_get_market_metrics(session, ["SPY", "AAPL"])


async def test_get_risk_free_rate_async(session: Session):
    await a_get_risk_free_rate(session)


def test_get_dividends(session: Session):
    get_dividends(session, "SPY")


def test_get_earnings(session: Session):
    get_earnings(session, "AAPL", date.today())


def test_get_market_metrics(session: Session):
    get_market_metrics(session, ["SPY", "AAPL"])


def test_get_risk_free_rate(session: Session):
    get_risk_free_rate(session)
