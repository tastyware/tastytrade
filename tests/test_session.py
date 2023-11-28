from datetime import datetime, timedelta

from tastytrade import CertificationSession
from tastytrade.dxfeed import EventType


def test_get_customer(session):
    assert session.get_customer() != {}


def test_get_event(session):
    session.get_event(EventType.QUOTE, ['SPY', 'AAPL'])


def test_get_time_and_sale(session):
    start_date = datetime.today() - timedelta(days=30)
    session.get_time_and_sale(['SPY', 'AAPL'], start_date)


def test_get_candle(session):
    start_date = datetime.today() - timedelta(days=30)
    session.get_candle(['SPY', 'AAPL'], '1d', start_date)


def test_destroy(get_cert_credentials):
    usr, pwd = get_cert_credentials
    session = CertificationSession(usr, pwd)
    assert session.destroy()
