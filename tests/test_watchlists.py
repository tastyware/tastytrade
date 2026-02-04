from time import sleep

import pytest
from pytest import fixture

from tastytrade import Session
from tastytrade.instruments import InstrumentType
from tastytrade.watchlists import PairsWatchlist, PrivateWatchlist, PublicWatchlist

WATCHLIST_NAME = "TestWatchlist"
pytestmark = pytest.mark.anyio


async def test_get_pairs_watchlists(session: Session):
    await PairsWatchlist.get(session)


async def test_get_pairs_watchlist(session: Session):
    await PairsWatchlist.get(session, "Stocks")


async def test_get_public_watchlists(session: Session):
    res = await PublicWatchlist.get(session)
    assert isinstance(res, list)


async def test_get_public_watchlist(session: Session):
    res = await PublicWatchlist.get(session, "Crypto")
    assert isinstance(res, PublicWatchlist)


async def test_get_private_watchlists(session: Session):
    res = await PrivateWatchlist.get(session)
    assert isinstance(res, list)


@fixture(scope="module")
def private_wl(anyio_backend: str) -> PrivateWatchlist:
    wl = PrivateWatchlist(name=WATCHLIST_NAME)
    wl.add_symbol("MSFT", InstrumentType.EQUITY)
    wl.add_symbol("AAPL", InstrumentType.EQUITY)
    return wl


async def test_upload_private_watchlist(session: Session, private_wl: PrivateWatchlist):
    await private_wl.upload(session)


async def test_get_private_watchlist(session: Session):
    sleep(1)
    res = await PrivateWatchlist.get(session, WATCHLIST_NAME)
    assert isinstance(res, PrivateWatchlist)


async def test_update_private_watchlist(session: Session, private_wl: PrivateWatchlist):
    private_wl.remove_symbol("MSFT", InstrumentType.EQUITY)
    sleep(1)
    await private_wl.update(session)


async def test_remove_private_watchlist(session: Session):
    sleep(1)
    await PrivateWatchlist.remove(session, WATCHLIST_NAME)
