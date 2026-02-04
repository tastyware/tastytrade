import pytest

from tastytrade import Session
from tastytrade.instruments import (
    Cryptocurrency,
    Equity,
    Future,
    FutureOption,
    FutureOptionProduct,
    FutureProduct,
    NestedFutureOptionChain,
    NestedOptionChain,
    Option,
    Warrant,
    get_future_option_chain,
    get_option_chain,
    get_quantity_decimal_precisions,
)

pytestmark = pytest.mark.anyio


async def test_get_cryptocurrency(session: Session):
    await Cryptocurrency.get(session, "ETH/USD")


async def test_get_cryptocurrencies(session: Session):
    await Cryptocurrency.get(session)


async def test_get_active_equities(session: Session):
    await Equity.get_active_equities(session, page_offset=0)


async def test_get_equities(session: Session):
    await Equity.get(session, ["AAPL", "SPY"])


async def test_get_equity(session: Session):
    await Equity.get(session, "AAPL")


async def test_get_futures(session: Session):
    futures = await Future.get(session, product_codes=["ES"])
    assert futures != []
    await Future.get(session, futures[0].symbol)


async def test_get_future_product(session: Session):
    await FutureProduct.get(session, "ZN")


async def test_get_future_option_product(session: Session):
    await FutureOptionProduct.get(session, "LO")


async def test_get_future_option_products(session: Session):
    await FutureOptionProduct.get(session)


async def test_get_future_products(session: Session):
    await FutureProduct.get(session)


async def test_get_nested_option_chain(session: Session):
    await NestedOptionChain.get(session, "SPY")


async def test_get_nested_future_option_chain(session: Session):
    await NestedFutureOptionChain.get(session, "ES")


async def test_get_warrants(session: Session):
    await Warrant.get(session)


async def test_get_warrant(session: Session):
    await Warrant.get(session, "NKLAW")


async def test_get_quantity_decimal_precisions(session: Session):
    await get_quantity_decimal_precisions(session)


async def test_get_option_chain(session: Session):
    chain = await get_option_chain(session, "SPY")
    assert chain != {}
    for options in chain.values():
        single = await Option.get(session, options[0].symbol)
        multiple = await Option.get(session, [options[0].symbol, options[1].symbol])
        assert isinstance(single, Option)
        assert isinstance(multiple, list)
        break


async def test_get_future_option_chain(session: Session):
    chain = await get_future_option_chain(session, "ES")
    assert chain != {}
    for options in chain.values():
        await FutureOption.get(session, options[0].symbol)
        symbols = [o.symbol for o in options[:4]]
        await FutureOption.get(session, symbols)
        break


def test_streamer_symbol_to_occ():
    dxf = ".SPY240324P480.5"
    occ = "SPY   240324P00480500"
    assert Option.streamer_symbol_to_occ(dxf) == occ


def test_occ_to_streamer_symbol():
    dxf = ".SPY240324P480.5"
    occ = "SPY   240324P00480500"
    assert Option.occ_to_streamer_symbol(occ) == dxf
