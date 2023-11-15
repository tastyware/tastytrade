from tastytrade.instruments import (Cryptocurrency, Equity,
                                    FutureOptionProduct, FutureProduct,
                                    NestedOptionChain, Option, Warrant,
                                    get_option_chain,
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


def test_get_warrants(session):
    Warrant.get_warrants(session)


def test_get_quantity_decimal_precisions(session):
    get_quantity_decimal_precisions(session)


def test_get_option_chain(session):
    chain = get_option_chain(session, 'SPY')
    symbols = []
    for options in chain.values():
        symbols.extend([o.symbol for o in options])
        break
    Option.get_option(session, symbols[0])
    Option.get_options(session, symbols)
