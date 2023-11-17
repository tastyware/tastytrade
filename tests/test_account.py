from decimal import Decimal

import pytest

from tastytrade import Account
from tastytrade.instruments import Equity
from tastytrade.order import (NewOrder, OrderAction, OrderTimeInForce,
                              OrderType, PriceEffect)


@pytest.fixture(scope='session')
def account(session):
    return Account.get_accounts(session)[1]


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
    symbol = Equity.get_equity(session, 'SPY')
    leg = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)

    return NewOrder(
        time_in_force=OrderTimeInForce.DAY,
        order_type=OrderType.LIMIT,
        legs=[leg],
        price=Decimal(42),  # if this fills the US has crumbled
        price_effect=PriceEffect.DEBIT
    )


@pytest.fixture(scope='session')
def placed_order(session, account, new_order):
    return account.place_order(session, new_order, dry_run=False).order


def test_place_and_delete_order(session, account, new_order):
    order = account.place_order(session, new_order, dry_run=False).order
    account.delete_order(session, order.id)


def test_get_order(session, account, placed_order):
    assert account.get_order(session, placed_order.id).id == placed_order.id


def test_replace_and_delete_order(session, account, new_order, placed_order):
    modified_order = new_order.copy()
    modified_order.price = Decimal(40)
    replaced = account.replace_order(session, placed_order.id, modified_order)
    account.delete_order(session, replaced.id)


def test_get_order_history(session, account):
    account.get_order_history(session, page_offset=0)


def test_get_live_orders(session, account):
    account.get_live_orders(session)
