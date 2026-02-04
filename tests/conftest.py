import os
from typing import Any

import pytest

from tastytrade import Session


@pytest.fixture(scope="module", params=["asyncio", "trio"])
def anyio_backend(request: Any) -> str:
    return request.param


@pytest.fixture(scope="function")
def session() -> Session:
    return Session(os.environ["TT_SECRET"], os.environ["TT_REFRESH"])


@pytest.fixture(scope="class")
def inject_credentials(request: Any) -> None:
    request.cls.credentials = os.environ["TT_SECRET"], os.environ["TT_REFRESH"]
