import os

from tastytrade import CertificationSession


def test_session():
    username = os.environ.get('TT_USERNAME', None)
    assert username is not None
    password = os.environ.get('TT_PASSWORD', None)
    assert password is not None

    session = CertificationSession(username, password)
