import os
from typing import AsyncGenerator

from pytest import fixture

from tastytrade import Session


# Run all tests with asyncio only
@fixture(scope="session")
def aiolib() -> str:
    return "asyncio"


@fixture(scope="session")
def credentials() -> tuple[str, str]:
    username = os.getenv("TT_USERNAME")
    password = os.getenv("TT_PASSWORD")
    assert username is not None
    assert password is not None
    return username, password


@fixture(scope="session")
async def session(
    credentials: tuple[str, str], aiolib: str
) -> AsyncGenerator[Session, None]:
    with Session(*credentials) as session:
        yield session


@fixture(scope="class")
def inject_credentials(request, credentials: tuple[str, str]):
    request.cls.credentials = credentials
