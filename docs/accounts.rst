Accounts
========

An account object contains information about a specific Tastytrade account. It can be used to place trades, monitor profit/loss, and analyze positions.

The easiest way to get an account is to grab all accounts associated with a specific session:

.. code-block:: python

   from tastytrade import Account
   accounts = await Account.get(session)

You can also get a specific account by its unique ID:

.. code-block:: python

   account = await Account.get(session, '5WX01234')

The ``get_balances`` function can be used to obtain information about the current buying power and cash balance:

.. code-block:: python

   balance = await account.get_balances(session)
   print(balance)

>>> account_number='5WX01234' cash_balance=Decimal('9371.91') long_equity_value=Decimal('16190.0') margin_equity=Decimal('25561.91') equity_buying_power=Decimal('36530.82') derivative_buying_power=Decimal('18265.41') maintenance_requirement=Decimal('7276.5') net_liquidating_value=Decimal('25561.91') cash_available_to_withdraw=Decimal('17825.41') day_trade_excess=Decimal('17825.41') cryptocurrency_margin_requirement=Decimal('0.00000138') closed_loop_available_balance=Decimal('17825.41') used_derivative_buying_power=Decimal('7276.5') snapshot_date=datetime.date(2026, 7, 2) reg_t_margin_requirement=Decimal('7276.50000138') maintenance_excess=Decimal('18265.41') effective_cryptocurrency_buying_power=Decimal('17825.41') updated_at=datetime.datetime(2026, 7, 2, 18, 20, 28, 807000, tzinfo=TzInfo(0))

To obtain information about current positions:

.. code-block:: python

   positions = await account.get_positions(session)
   print(positions[0])

>>> account_number='5WX01234' symbol='BRK/B' instrument_type=<InstrumentType.EQUITY: 'Equity'> underlying_symbol='BRK/B' quantity=Decimal('1') quantity_direction='Long' close_price=Decimal('499.74') average_open_price=Decimal('477.34') multiplier=Decimal('1.0') cost_effect='Credit' created_at=datetime.datetime(2026, 4, 17, 14, 23, 1, 210000, tzinfo=TzInfo(0)) updated_at=datetime.datetime(2026, 6, 9, 20, 2, 32, 427000, tzinfo=TzInfo(0)) average_yearly_market_close_price=Decimal('477.34') average_daily_market_close_price=Decimal('499.74') realized_day_gain_date=datetime.date(2026, 6, 9) realized_today_date=datetime.date(2026, 6, 9)

To fetch a list of past transactions:

.. code-block:: python

   history = await account.get_history(session, start_date=date(2024, 1, 1))
   print(history[-1])

>>> id=386679165 account_number='5WX01234' transaction_type='Money Movement' transaction_sub_type='Balance Adjustment' description='Regulatory fee adjustment' executed_at=datetime.datetime(2025, 9, 13, 19, 19, 18, 891000, tzinfo=TzInfo(0)) transaction_date=datetime.date(2025, 9, 13) value=Decimal('0.009') net_value=Decimal('0.009') is_estimated_fee=True

We can also view portfolio P/L over time (and even plot it!):

.. code-block:: python

   import matplotlib.pyplot as plt
   nl = await account.get_net_liquidating_value_history(session, time_back='1m')  # past 1 month
   plt.plot([n.time for n in nl], [n.close for n in nl])
   plt.show()

.. image:: img/netliq.png
  :width: 640
  :alt: P/L graph

Accounts are needed to place, replace, and delete orders. See more in :doc:`Orders <orders>`.

There are many more things you can do with an :class:`~tastytrade.account.Account` object--check out the SDK Reference section!
