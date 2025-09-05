import os
from typing import Any

from pytest import fixture

from tastytrade import Session


# Run all tests with asyncio only
@fixture(scope="session")
def aiolib() -> str:
    return "asyncio"


@fixture(scope="session")
async def session(aiolib: str) -> Session:
    return Session(os.environ["TT_SECRET"], os.environ["TT_REFRESH"])


@fixture(scope="class")
def inject_credentials(request: Any) -> None:
    request.cls.credentials = os.environ["TT_SECRET"], os.environ["TT_REFRESH"]
