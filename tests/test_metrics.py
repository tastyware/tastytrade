from datetime import date

from tastytrade.metrics import (get_dividends, get_earnings,
                                get_market_metrics, get_risk_free_rate)


def test_get_dividends(session):
    get_dividends(session, 'SPY')


def test_get_earnings(session):
    get_earnings(session, 'AAPL', date.today())


def test_get_market_metrics(session):
    get_market_metrics(session, ['SPY', 'AAPL'])


def test_get_risk_free_rate(session):
    get_risk_free_rate(session)
