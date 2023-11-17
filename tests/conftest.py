import os

import pytest

from tastytrade import ProductionSession


@pytest.fixture(scope='session')
def session():
    username = os.environ.get('TT_USERNAME', None)
    password = os.environ.get('TT_PASSWORD', None)

    assert username is not None
    assert password is not None

    session = ProductionSession(username, password)
    yield session

    session.destroy()
