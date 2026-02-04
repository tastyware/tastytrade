import pytest
from anyio import sleep

from tastytrade.market_data import (
    get_market_data,
    get_market_data_by_type,
)
from tastytrade.order import InstrumentType
from tastytrade.session import Session

pytestmark = pytest.mark.anyio


async def test_get_market_data(session: Session):
    await sleep(1)  # to not get rate limited
    await get_market_data(session, "VIX", InstrumentType.INDEX)


async def test_get_market_data_by_type(session: Session):
    await get_market_data_by_type(
        session,
        indices=["SPX", "VIX"],
        cryptocurrencies=["ETH/USD", "BTC/USD"],
        equities=["SPLG", "SPY"],
    )
