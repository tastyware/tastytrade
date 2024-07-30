from decimal import Decimal
from time import sleep

import pytest

from tastytrade import Account, Session
from tastytrade.instruments import Equity
from tastytrade.order import (NewComplexOrder, NewOrder, OrderAction,
                              OrderTimeInForce, OrderType, PriceEffect)


@pytest.fixture(scope='session')
def account(session):
    return Account.get_accounts(session)[0]


@pytest.fixture
def cert_session(get_cert_credentials):
    usr, pwd = get_cert_credentials
    session = Session(usr, pwd, is_test=True)
    yield session
    session.destroy()


def test_cert_accounts(cert_session):
    assert Account.get_accounts(cert_session) != []


def test_get_account(session, account):
    acc = Account.get_account(session, account.account_number)
    assert acc == account


def test_get_trading_status(session, account):
    account.get_trading_status(session)


def test_get_balances(session, account):
    account.get_balances(session)


def test_get_balance_snapshots(session, account):
    account.get_balance_snapshots(session)


def test_get_positions(session, account):
    account.get_positions(session)


def test_get_history(session, account):
    account.get_history(session, page_offset=0)


def test_get_total_fees(session, account):
    account.get_total_fees(session)


def test_get_position_limit(session, account):
    account.get_position_limit(session)


def test_get_margin_requirements(session, account):
    account.get_margin_requirements(session)


def test_get_net_liquidating_value_history(session, account):
    account.get_net_liquidating_value_history(session, time_back='1y')


def test_get_effective_margin_requirements(session, account):
    account.get_effective_margin_requirements(session, 'SPY')


@pytest.fixture(scope='session')
def new_order(session):
    symbol = Equity.get_equity(session, 'F')
    leg = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)

    return NewOrder(
        time_in_force=OrderTimeInForce.DAY,
        order_type=OrderType.LIMIT,
        legs=[leg],
        price=Decimal(3),
        price_effect=PriceEffect.DEBIT
    )


@pytest.fixture(scope='session')
def placed_order(session, account, new_order):
    return account.place_order(session, new_order, dry_run=False).order


def test_get_order(session, account, placed_order):
    sleep(3)
    assert account.get_order(session, placed_order.id).id == placed_order.id


def test_replace_and_delete_order(session, account, new_order, placed_order):
    modified_order = new_order.model_copy()
    modified_order.price = Decimal('3.01')
    replaced = account.replace_order(session, placed_order.id, modified_order)
    sleep(3)
    account.delete_order(session, replaced.id)


def test_get_order_history(session, account):
    account.get_order_history(session, page_offset=0)


def test_get_complex_order_history(session, account):
    account.get_complex_order_history(session, page_offset=0)


def test_get_live_orders(session, account):
    account.get_live_orders(session)


def test_place_oco_order(session, account):
    """
    # account must have a share of F for this to work
    symbol = Equity.get_equity(session, 'F')
    closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE)
    oco = NewComplexOrder(
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal('100'),  # will never fill
                price_effect=PriceEffect.CREDIT
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal('3'),  # will never fill
                price_effect=PriceEffect.CREDIT
            )
        ]
    )
    resp2 = account.place_complex_order(session, oco, dry_run=False)
    sleep(3)
    # test get complex order
    _ = account.get_complex_order(session, resp2.complex_order.id)
    account.delete_complex_order(session, resp2.complex_order.id)
    """
    assert True


def test_place_otoco_order(session, account):
    symbol = Equity.get_equity(session, 'AAPL')
    opening = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)
    closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE)
    otoco = NewComplexOrder(
        trigger_order=NewOrder(
            time_in_force=OrderTimeInForce.DAY,
            order_type=OrderType.LIMIT,
            legs=[opening],
            price=Decimal('100'),  # won't fill
            price_effect=PriceEffect.DEBIT
        ),
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal('400'),  # won't fill
                price_effect=PriceEffect.CREDIT
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal('25'),  # won't fill
                price_effect=PriceEffect.CREDIT
            )
        ]
    )
    resp = account.place_complex_order(session, otoco, dry_run=False)
    sleep(3)
    account.delete_complex_order(session, resp.complex_order.id)


def test_get_live_complex_orders(session, account):
    orders = account.get_live_complex_orders(session)
    assert orders != []
