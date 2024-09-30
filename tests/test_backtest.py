from datetime import timedelta

import pytest

from tastytrade import today_in_new_york
from tastytrade.backtest import (
    Backtest,
    BacktestEntry,
    BacktestExit,
    BacktestLeg,
    BacktestSession,
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_backtest_simple(session):
    backtest_session = BacktestSession(session)
    backtest = Backtest(
        symbol="SPY",
        entry_conditions=BacktestEntry(),
        exit_conditions=BacktestExit(at_days_to_expiration=21),
        legs=[BacktestLeg(), BacktestLeg(side="put")],
        start_date=today_in_new_york() - timedelta(days=365),
    )
    results = [r async for r in backtest_session.run(backtest)]
    assert results[-1].status == "completed"
