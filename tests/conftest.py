import os
import pytest

from tastytrade import CertificationSession


@pytest.fixture(scope='session')
def session():
    username = os.environ.get('TT_USERNAME', None)
    password = os.environ.get('TT_PASSWORD', None)

    session = CertificationSession(username, password)
    yield session

    session.destroy()
