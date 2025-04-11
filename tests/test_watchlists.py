from time import sleep

from pytest import fixture

from tastytrade import Session
from tastytrade.instruments import InstrumentType
from tastytrade.watchlists import PairsWatchlist, PrivateWatchlist, PublicWatchlist

WATCHLIST_NAME = "TestWatchlist"


def test_get_pairs_watchlists(session: Session):
    PairsWatchlist.get(session)


def test_get_pairs_watchlist(session: Session):
    PairsWatchlist.get(session, "Stocks")


async def test_get_pairs_watchlists_async(session: Session):
    await PairsWatchlist.a_get(session)


async def test_get_pairs_watchlist_async(session: Session):
    await PairsWatchlist.a_get(session, "Stocks")


def test_get_public_watchlists(session: Session):
    res = PublicWatchlist.get(session)
    assert isinstance(res, list)


def test_get_public_watchlist(session: Session):
    res = PublicWatchlist.get(session, "Crypto")
    assert isinstance(res, PublicWatchlist)


def test_get_private_watchlists(session: Session):
    res = PrivateWatchlist.get(session)
    assert isinstance(res, list)


async def test_get_public_watchlists_async(session: Session):
    res = await PublicWatchlist.a_get(session)
    assert isinstance(res, list)


async def test_get_public_watchlist_async(session: Session):
    res = await PublicWatchlist.a_get(session, "Crypto")
    assert isinstance(res, PublicWatchlist)


async def test_get_private_watchlists_async(session: Session):
    res = await PrivateWatchlist.a_get(session)
    assert isinstance(res, list)


@fixture(scope="module")
def private_wl() -> PrivateWatchlist:
    wl = PrivateWatchlist(name=WATCHLIST_NAME)
    wl.add_symbol("MSFT", InstrumentType.EQUITY)
    wl.add_symbol("AAPL", InstrumentType.EQUITY)
    return wl


def test_upload_private_watchlist(session: Session, private_wl: PrivateWatchlist):
    private_wl.upload(session)


def test_get_private_watchlist(session: Session):
    sleep(1)
    res = PrivateWatchlist.get(session, WATCHLIST_NAME)
    assert isinstance(res, PrivateWatchlist)


def test_update_private_watchlist(session: Session, private_wl: PrivateWatchlist):
    private_wl.remove_symbol("AAPL", InstrumentType.EQUITY)
    sleep(1)
    private_wl.update(session)


def test_remove_private_watchlist(session: Session):
    sleep(1)
    PrivateWatchlist.remove(session, WATCHLIST_NAME)


async def test_upload_private_watchlist_async(
    session: Session, private_wl: PrivateWatchlist
):
    await private_wl.a_upload(session)


async def test_get_private_watchlist_async(session: Session):
    sleep(1)
    res = await PrivateWatchlist.a_get(session, WATCHLIST_NAME)
    assert isinstance(res, PrivateWatchlist)


async def test_update_private_watchlist_async(
    session: Session, private_wl: PrivateWatchlist
):
    private_wl.remove_symbol("MSFT", InstrumentType.EQUITY)
    sleep(1)
    await private_wl.a_update(session)


async def test_remove_private_watchlist_async(session: Session):
    sleep(1)
    await PrivateWatchlist.a_remove(session, WATCHLIST_NAME)
