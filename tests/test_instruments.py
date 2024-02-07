from tastytrade.instruments import (Cryptocurrency, Equity, Future,
                                    FutureOption, FutureOptionProduct,
                                    FutureProduct, NestedFutureOptionChain,
                                    NestedOptionChain, Option, Warrant,
                                    get_future_option_chain, get_option_chain,
                                    get_quantity_decimal_precisions)


def test_get_cryptocurrency(session):
    Cryptocurrency.get_cryptocurrency(session, 'ETH/USD')


def test_get_cryptocurrencies(session):
    Cryptocurrency.get_cryptocurrencies(session)


def test_get_active_equities(session):
    Equity.get_active_equities(session, page_offset=0)


def test_get_equities(session):
    Equity.get_equities(session, ['AAPL', 'SPY'])


def test_get_equity(session):
    Equity.get_equity(session, 'AAPL')


def test_get_futures(session):
    futures = Future.get_futures(session, product_codes=['ES'])
    Future.get_future(session, futures[0].symbol)


def test_get_future_product(session):
    FutureProduct.get_future_product(session, 'ZN')


def test_get_future_option_product(session):
    FutureOptionProduct.get_future_option_product(session, 'LO')


def test_get_future_option_products(session):
    FutureOptionProduct.get_future_option_products(session)


def test_get_future_products(session):
    FutureProduct.get_future_products(session)


def test_get_nested_option_chain(session):
    NestedOptionChain.get_chain(session, 'SPY')


def test_get_nested_future_option_chain(session):
    NestedFutureOptionChain.get_chain(session, 'ES')


def test_get_warrants(session):
    Warrant.get_warrants(session)


def test_get_warrant(session):
    Warrant.get_warrant(session, 'NKLAW')


def test_get_quantity_decimal_precisions(session):
    get_quantity_decimal_precisions(session)


def test_get_option_chain(session):
    chain = get_option_chain(session, 'SPY')
    for options in chain.values():
        Option.get_option(session, options[0].symbol)
        break


def test_get_future_option_chain(session):
    chain = get_future_option_chain(session, 'ES')
    for options in chain.values():
        FutureOption.get_future_option(session, options[0].symbol)
        FutureOption.get_future_options(session, options[:4])
        break


def test_streamer_symbol_to_occ():
    dxf = '.SPY240324P480.5'
    occ = 'SPY   240324P00480500'
    assert Option.streamer_symbol_to_occ(dxf) == occ


def test_occ_to_streamer_symbol():
    dxf = '.SPY240324P480.5'
    occ = 'SPY   240324P00480500'
    assert Option.occ_to_streamer_symbol(occ) == dxf
