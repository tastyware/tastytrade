import os

from tastytrade import CertificationSession


def test_get_customer(session):
    assert session.get_customer() != {}


def test_destroy():
    # here we create a new session to avoid destroying the active one
    username = os.environ.get('TT_USERNAME', None)
    password = os.environ.get('TT_PASSWORD', None)

    session = CertificationSession(username, password)
    assert session.destroy()
