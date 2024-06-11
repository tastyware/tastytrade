import os

import pytest

from tastytrade import ProductionSession

CERT_USERNAME = 'tastyware'
CERT_PASSWORD = ':4s-S9/9L&Q~C]@v'


@pytest.fixture(scope='session')
def get_cert_credentials():
    return CERT_USERNAME, CERT_PASSWORD


@pytest.fixture(scope='session')
def session():
    username = os.environ.get('TT_USERNAME', None)
    password = os.environ.get('TT_PASSWORD', None)
    assert username is not None
    assert password is not None

    session = ProductionSession(username, password)
    yield session
    session.destroy()
