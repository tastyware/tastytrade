from tastytrade.metrics import get_risk_free_rate


def test_get_risk_free_rate(session):
    get_risk_free_rate(session)
