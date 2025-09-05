import os

import pytest
from proxy import TestCase

from tastytrade import Session


def test_get_customer(session: Session):
    session.get_customer()


async def test_get_customer_async(session: Session):
    await session.a_get_customer()


def test_serialize_deserialize(session: Session):
    data = session.serialize()
    obj = Session.deserialize(data)
    assert set(obj.__dict__.keys()) == set(session.__dict__.keys())


@pytest.mark.usefixtures("inject_credentials")
class TestProxy(TestCase):
    def test_session_with_proxy(self):
        assert self.PROXY is not None
        session = Session(
            *self.credentials,  # type: ignore
            proxy=f"http://127.0.0.1:{self.PROXY.flags.port}",
        )
        assert session.validate()


def test_cert_session():
    secret = os.getenv("TT_SECRET_SANDBOX")
    refresh = os.getenv("TT_REFRESH_SANDBOX")
    assert secret and refresh
    _ = Session(secret, refresh, is_test=True)


async def test_oauth_refresh_async(session: Session):
    await session.a_refresh()
