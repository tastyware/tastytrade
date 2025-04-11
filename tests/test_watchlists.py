from time import sleep

from pytest import fixture

from tastytrade import Session
from tastytrade.instruments import InstrumentType
from tastytrade.watchlists import PairsWatchlist, Watchlist

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
    Watchlist.get_public(session)


def test_get_public_watchlist(session: Session):
    Watchlist.get_public(session, "Crypto")


def test_get_private_watchlists(session: Session):
    Watchlist.get_private(session)


async def test_get_public_watchlists_async(session: Session):
    await Watchlist.a_get_public(session)


async def test_get_public_watchlist_async(session: Session):
    await Watchlist.a_get_public(session, "Crypto")


async def test_get_private_watchlists_async(session: Session):
    await Watchlist.a_get_private(session)


@fixture(scope="module")
def private_wl() -> Watchlist:
    wl = Watchlist(name=WATCHLIST_NAME)
    wl.add_symbol("MSFT", InstrumentType.EQUITY)
    wl.add_symbol("AAPL", InstrumentType.EQUITY)
    return wl


def test_upload_private_watchlist(session: Session, private_wl: Watchlist):
    private_wl.upload_private(session)


def test_get_private_watchlist(session: Session):
    sleep(1)
    Watchlist.get_private(session, WATCHLIST_NAME)


def test_update_private_watchlist(session: Session, private_wl: Watchlist):
    private_wl.remove_symbol("AAPL", InstrumentType.EQUITY)
    sleep(1)
    private_wl.update_private(session)


def test_remove_private_watchlist(session: Session):
    sleep(1)
    Watchlist.remove_private(session, WATCHLIST_NAME)


async def test_upload_private_watchlist_async(session: Session, private_wl: Watchlist):
    await private_wl.a_upload_private(session)


async def test_get_private_watchlist_async(session: Session):
    sleep(1)
    await Watchlist.a_get_private(session, WATCHLIST_NAME)


async def test_update_private_watchlist_async(session: Session, private_wl: Watchlist):
    private_wl.remove_symbol("MSFT", InstrumentType.EQUITY)
    sleep(1)
    await private_wl.a_update_private(session)


async def test_remove_private_watchlist_async(session: Session):
    sleep(1)
    await Watchlist.a_remove_private(session, WATCHLIST_NAME)
