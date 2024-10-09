import os

from pytest import fixture

from tastytrade import Session


# Run all tests with asyncio only
@fixture(scope="session")
def aiolib():
    return "asyncio"


@fixture(scope="session")
def credentials():
    username = os.getenv("TT_USERNAME")
    password = os.getenv("TT_PASSWORD")
    assert username is not None
    assert password is not None
    return username, password


@fixture(scope="session")
async def session(credentials, aiolib):
    session = Session(*credentials)
    yield session
    session.destroy()
