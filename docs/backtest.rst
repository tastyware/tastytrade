Backtesting
===========

Backtesting is a beta feature recently added to Tastytrade, so please report any issues!

Let's see how to perform a backtest:

.. code-block:: python

   from datetime import timedelta
   from tastytrade.backtest import (
       Backtest,
       BacktestEntry,
       BacktestExit,
       BacktestLeg,
       BacktestSession,
       today_in_new_york
    )
    from tqdm.asyncio import tqdm  # progress bar
    backtest_session = BacktestSession(session)
    backtest = Backtest(
        symbol="SPY",
        entry_conditions=BacktestEntry(),
        exit_conditions=BacktestExit(at_days_to_expiration=21),
        legs=[BacktestLeg(), BacktestLeg(side="put")],
        start_date=today_in_new_york() - timedelta(days=365)
    )
    results = [r async for r in tqdm(backtest_session.run(backtest))]
    print(results[-1])

There are lots of configuration options you can find in the documentation for each class.
The ``run`` function is an ``AsyncGenerator``, so you can do something else while a backtest is running, show a progress bar, or maybe even run several at once!
