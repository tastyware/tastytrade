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
    a_get_future_option_chain,
    a_get_option_chain,
    a_get_quantity_decimal_precisions,
    get_future_option_chain,
    get_option_chain,
    get_quantity_decimal_precisions,
)


async def test_get_cryptocurrency_async(session: Session):
    await Cryptocurrency.a_get(session, "ETH/USD")


def test_get_cryptocurrency(session: Session):
    Cryptocurrency.get(session, "ETH/USD")


async def test_get_cryptocurrencies_async(session: Session):
    await Cryptocurrency.a_get(session)


def test_get_cryptocurrencies(session: Session):
    Cryptocurrency.get(session)


async def test_get_active_equities_async(session: Session):
    await Equity.a_get_active_equities(session, page_offset=0)


def test_get_active_equities(session: Session):
    Equity.get_active_equities(session, page_offset=0)


async def test_get_equities_async(session: Session):
    await Equity.a_get(session, ["AAPL", "SPY"])


def test_get_equities(session: Session):
    Equity.get(session, ["AAPL", "SPY"])


async def test_get_equity_async(session: Session):
    await Equity.a_get(session, "AAPL")


def test_get_equity(session: Session):
    Equity.get(session, "AAPL")


async def test_get_futures_async(session: Session):
    futures = await Future.a_get(session, product_codes=["ES"])
    assert futures != []
    await Future.a_get(session, futures[0].symbol)


def test_get_futures(session: Session):
    futures = Future.get(session, product_codes=["ES"])
    assert futures != []
    Future.get(session, futures[0].symbol)


async def test_get_future_product_async(session: Session):
    await FutureProduct.a_get(session, "ZN")


def test_get_future_product(session: Session):
    FutureProduct.get(session, "ZN")


async def test_get_future_option_product_async(session: Session):
    await FutureOptionProduct.a_get(session, "LO")


def test_get_future_option_product(session: Session):
    FutureOptionProduct.get(session, "LO")


async def test_get_future_option_products_async(session: Session):
    await FutureOptionProduct.a_get(session)


def test_get_future_option_products(session: Session):
    FutureOptionProduct.get(session)


async def test_get_future_products_async(session: Session):
    await FutureProduct.a_get(session)


def test_get_future_products(session: Session):
    FutureProduct.get(session)


async def test_get_nested_option_chain_async(session: Session):
    await NestedOptionChain.a_get(session, "SPY")


def test_get_nested_option_chain(session: Session):
    NestedOptionChain.get(session, "SPY")


async def test_get_nested_future_option_chain_async(session: Session):
    await NestedFutureOptionChain.a_get(session, "ES")


def test_get_nested_future_option_chain(session: Session):
    NestedFutureOptionChain.get(session, "ES")


async def test_get_warrants_async(session: Session):
    await Warrant.a_get(session)


def test_get_warrants(session: Session):
    Warrant.get(session)


async def test_get_warrant_async(session: Session):
    await Warrant.a_get(session, "NKLAW")


def test_get_warrant(session: Session):
    Warrant.get(session, "NKLAW")


async def test_get_quantity_decimal_precisions_async(session: Session):
    await a_get_quantity_decimal_precisions(session)


def test_get_quantity_decimal_precisions(session: Session):
    get_quantity_decimal_precisions(session)


async def test_get_option_chain_async(session: Session):
    chain = await a_get_option_chain(session, "SPY")
    assert chain != {}
    for options in chain.values():
        await Option.a_get(session, options[0].symbol)
        break


def test_get_option_chain(session: Session):
    chain = get_option_chain(session, "SPY")
    assert chain != {}
    for options in chain.values():
        Option.get(session, options[0].symbol)
        break


async def test_get_future_option_chain_async(session: Session):
    chain = await a_get_future_option_chain(session, "ES")
    assert chain != {}
    for options in chain.values():
        await FutureOption.a_get(session, options[0].symbol)
        symbols = [o.symbol for o in options[:4]]
        await FutureOption.a_get(session, symbols)
        break


def test_get_future_option_chain(session: Session):
    chain = get_future_option_chain(session, "ES")
    assert chain != {}
    for options in chain.values():
        FutureOption.get(session, options[0].symbol)
        symbols = [o.symbol for o in options[:4]]
        FutureOption.get(session, symbols)
        break


def test_streamer_symbol_to_occ():
    dxf = ".SPY240324P480.5"
    occ = "SPY   240324P00480500"
    assert Option.streamer_symbol_to_occ(dxf) == occ


def test_occ_to_streamer_symbol():
    dxf = ".SPY240324P480.5"
    occ = "SPY   240324P00480500"
    assert Option.occ_to_streamer_symbol(occ) == dxf
