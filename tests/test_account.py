import os
from datetime import datetime
from decimal import Decimal
from time import sleep

from pytest import fixture

from tastytrade import Account
from tastytrade.instruments import Equity
from tastytrade.order import (
    NewComplexOrder,
    NewOrder,
    OrderAction,
    OrderTimeInForce,
    OrderType,
)


@fixture(scope="module")
def account_number():
    account_number = os.getenv("TT_ACCOUNT")
    assert account_number is not None
    return account_number


@fixture(scope="module")
async def account(session, account_number, aiolib):
    return Account.get_account(session, account_number)


def test_get_account(account):
    pass


def test_get_accounts(session):
    assert Account.get_accounts(session) != []


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
    account.get_net_liquidating_value_history(session, time_back="1y")


def test_get_effective_margin_requirements(session, account):
    account.get_effective_margin_requirements(session, "SPY")


def test_get_order_history(session, account):
    account.get_order_history(session, page_offset=0)


def test_get_complex_order_history(session, account):
    account.get_complex_order_history(session, page_offset=0)


def test_get_live_orders(session, account):
    account.get_live_orders(session)


async def test_get_account_async(session, account_number):
    await Account.a_get_account(session, account_number)


async def test_get_accounts_async(session):
    accounts = await Account.a_get_accounts(session)
    assert accounts != []


async def test_get_trading_status_async(session, account):
    await account.a_get_trading_status(session)


async def test_get_balances_async(session, account):
    await account.a_get_balances(session)


async def test_get_balance_snapshots_async(session, account):
    await account.a_get_balance_snapshots(session)


async def test_get_positions_async(session, account):
    await account.a_get_positions(session)


async def test_get_history_async(session, account):
    await account.a_get_history(session, page_offset=0)


async def test_get_total_fees_async(session, account):
    await account.a_get_total_fees(session)


async def test_get_position_limit_async(session, account):
    await account.a_get_position_limit(session)


async def test_get_margin_requirements_async(session, account):
    await account.a_get_margin_requirements(session)


async def test_get_net_liquidating_value_history_async(session, account):
    await account.a_get_net_liquidating_value_history(session, time_back="1y")


async def test_get_effective_margin_requirements_async(session, account):
    await account.a_get_effective_margin_requirements(session, "SPY")


async def test_get_order_history_async(session, account):
    await account.a_get_order_history(session, page_offset=0)


async def test_get_complex_order_history_async(session, account):
    await account.a_get_complex_order_history(session, page_offset=0)


async def test_get_live_orders_async(session, account):
    await account.a_get_live_orders(session)


def test_get_order_chains(session, account):
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    end_time = datetime.now()
    account.get_order_chains(session, "F", start_time=start_time, end_time=end_time)


async def test_get_order_chains_async(session, account):
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    end_time = datetime.now()
    await account.a_get_order_chains(
        session, "F", start_time=start_time, end_time=end_time
    )


@fixture(scope="module")
def new_order(session):
    symbol = Equity.get_equity(session, "F")
    leg = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)
    return NewOrder(
        time_in_force=OrderTimeInForce.DAY,
        order_type=OrderType.LIMIT,
        legs=[leg],
        price=Decimal(-2),
    )


@fixture(scope="module")
def placed_order(session, account, new_order):
    return account.place_order(session, new_order, dry_run=False).order


def test_place_order(placed_order):
    pass


def test_get_order(session, account, placed_order):
    sleep(3)
    assert account.get_order(session, placed_order.id).id == placed_order.id


def test_replace_and_delete_order(session, account, new_order, placed_order):
    modified_order = new_order.model_copy()
    modified_order.price = Decimal("-2.01")
    replaced = account.replace_order(session, placed_order.id, modified_order)
    sleep(3)
    account.delete_order(session, replaced.id)


def test_place_oco_order(session, account):
    # account must have a share of F for this to work
    symbol = Equity.get_equity(session, "F")
    closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE)
    oco = NewComplexOrder(
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal("100"),  # will never fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal("1.5"),  # will never fill
            ),
        ]
    )
    resp2 = account.place_complex_order(session, oco, dry_run=False)
    sleep(3)
    # test get complex order
    _ = account.get_complex_order(session, resp2.complex_order.id)
    account.delete_complex_order(session, resp2.complex_order.id)


def test_place_otoco_order(session, account):
    symbol = Equity.get_equity(session, "AAPL")
    opening = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)
    closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE)
    otoco = NewComplexOrder(
        trigger_order=NewOrder(
            time_in_force=OrderTimeInForce.DAY,
            order_type=OrderType.LIMIT,
            legs=[opening],
            price=Decimal("-2"),  # won't fill
        ),
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal("400"),  # won't fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal("1.5"),  # won't fill
            ),
        ],
    )
    resp = account.place_complex_order(session, otoco, dry_run=False)
    sleep(3)
    account.delete_complex_order(session, resp.complex_order.id)


def test_get_live_complex_orders(session, account):
    orders = account.get_live_complex_orders(session)
    assert orders != []


@fixture(scope="module")
async def placed_order_async(session, account, new_order):
    res = await account.a_place_order(session, new_order, dry_run=False)
    return res.order


async def test_place_order_async(placed_order_async):
    pass


async def test_get_order_async(session, account, placed_order_async):
    sleep(3)
    placed = await account.a_get_order(session, placed_order_async.id)
    assert placed.id == placed_order_async.id


async def test_replace_and_delete_order_async(
    session, account, new_order, placed_order_async
):
    modified_order = new_order.model_copy()
    modified_order.price = Decimal("-2.01")
    replaced = await account.a_replace_order(
        session, placed_order_async.id, modified_order
    )
    sleep(3)
    await account.a_delete_order(session, replaced.id)


async def test_place_complex_order_async(session, account):
    sleep(3)
    symbol = Equity.get_equity(session, "AAPL")
    opening = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN)
    closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE)
    otoco = NewComplexOrder(
        trigger_order=NewOrder(
            time_in_force=OrderTimeInForce.DAY,
            order_type=OrderType.LIMIT,
            legs=[opening],
            price=Decimal("-2"),  # won't fill
        ),
        orders=[
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.LIMIT,
                legs=[closing],
                price=Decimal("400"),  # won't fill
            ),
            NewOrder(
                time_in_force=OrderTimeInForce.GTC,
                order_type=OrderType.STOP,
                legs=[closing],
                stop_trigger=Decimal("1.5"),  # won't fill
            ),
        ],
    )
    resp = await account.a_place_complex_order(session, otoco, dry_run=False)
    sleep(3)
    await account.a_delete_complex_order(session, resp.complex_order.id)


async def test_get_live_complex_orders_async(session, account):
    orders = await account.a_get_live_complex_orders(session)
    assert orders != []
