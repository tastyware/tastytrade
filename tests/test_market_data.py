import asyncio

from tastytrade.market_data import (
    a_get_market_data,
    a_get_market_data_by_type,
    get_market_data,
    get_market_data_by_type,
)
from tastytrade.order import InstrumentType
from tastytrade.session import Session


def test_get_market_data(session: Session):
    get_market_data(session, "SPX", InstrumentType.INDEX)


async def test_get_market_data_async(session: Session):
    await asyncio.sleep(1)  # to not get rate limited
    await a_get_market_data(session, "VIX", InstrumentType.INDEX)


def test_get_market_data_by_type(session: Session):
    get_market_data_by_type(
        session,
        indices=["SPX", "VIX"],
        cryptocurrencies=["ETH/USD", "BTC/USD"],
        equities=["SPLG", "SPY"],
    )


async def test_get_market_data_by_type_async(session: Session):
    await a_get_market_data_by_type(
        session,
        indices=["SPX", "VIX"],
        cryptocurrencies=["ETH/USD", "BTC/USD"],
        equities=["SPLG", "SPY"],
    )
