from datetime import timedelta

from tastytrade.backtest import (
    Backtest,
    BacktestEntry,
    BacktestExit,
    BacktestLeg,
    BacktestSession,
)
from tastytrade.utils import today_in_new_york


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
