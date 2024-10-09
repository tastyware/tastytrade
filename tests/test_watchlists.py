from time import sleep

from pytest import fixture

from tastytrade.instruments import InstrumentType
from tastytrade.watchlists import PairsWatchlist, Watchlist

WATCHLIST_NAME = "TestWatchlist"


def test_get_pairs_watchlists(session):
    PairsWatchlist.get_pairs_watchlists(session)


def test_get_pairs_watchlist(session):
    PairsWatchlist.get_pairs_watchlist(session, "Stocks")


async def test_get_pairs_watchlists_async(session):
    await PairsWatchlist.a_get_pairs_watchlists(session)


async def test_get_pairs_watchlist_async(session):
    await PairsWatchlist.a_get_pairs_watchlist(session, "Stocks")


def test_get_public_watchlists(session):
    Watchlist.get_public_watchlists(session)


def test_get_public_watchlist(session):
    Watchlist.get_public_watchlist(session, "Crypto")


def test_get_private_watchlists(session):
    Watchlist.get_private_watchlists(session)


async def test_get_public_watchlists_async(session):
    await Watchlist.a_get_public_watchlists(session)


async def test_get_public_watchlist_async(session):
    await Watchlist.a_get_public_watchlist(session, "Crypto")


async def test_get_private_watchlists_async(session):
    await Watchlist.a_get_private_watchlists(session)


@fixture(scope="module")
def private_wl():
    wl = Watchlist(name=WATCHLIST_NAME)
    wl.add_symbol("MSFT", InstrumentType.EQUITY)
    wl.add_symbol("AAPL", InstrumentType.EQUITY)
    return wl


def test_upload_private_watchlist(session, private_wl):
    private_wl.upload_private_watchlist(session)


def test_get_private_watchlist(session):
    sleep(1)
    Watchlist.get_private_watchlist(session, WATCHLIST_NAME)


def test_update_private_watchlist(session, private_wl):
    private_wl.remove_symbol("AAPL", InstrumentType.EQUITY)
    sleep(1)
    private_wl.update_private_watchlist(session)


def test_remove_private_watchlist(session):
    sleep(1)
    Watchlist.remove_private_watchlist(session, WATCHLIST_NAME)


async def test_upload_private_watchlist_async(session, private_wl):
    await private_wl.a_upload_private_watchlist(session)


async def test_get_private_watchlist_async(session):
    sleep(1)
    await Watchlist.a_get_private_watchlist(session, WATCHLIST_NAME)


async def test_update_private_watchlist_async(session, private_wl):
    private_wl.remove_symbol("MSFT", InstrumentType.EQUITY)
    sleep(1)
    await private_wl.a_update_private_watchlist(session)


async def test_remove_private_watchlist_async(session):
    sleep(1)
    await Watchlist.a_remove_private_watchlist(session, WATCHLIST_NAME)
