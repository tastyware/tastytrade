import os
from typing import Any, AsyncGenerator

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
def inject_credentials(request: Any, credentials: tuple[str, str]):
    request.cls.credentials = credentials


@fixture(scope="session")
def get_tastytrade_json():
    import json
    from pathlib import Path

    def _get_tastytrade_json(name: str) -> Any:
        path = (
            Path(__file__).parent.parent
            / "docs/tastytrade_api_examples"
            / "responses"
            / f"{name}.json"
        )
        with open(path) as f:
            return json.load(f)

    return _get_tastytrade_json
