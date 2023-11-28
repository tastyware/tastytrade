Accounts
========

An account object contains information about a specific Tastytrade account. It can be used to place trades, monitor profit/loss, and analyze positions.

The easiest way to get an account is to grab all accounts associated with a specific session:

.. code-block:: python

   from tastytrade import Account
   accounts = Account.get_accounts(session)

You can also get a specific account by its unique ID:

.. code-block:: python

   account = Account.get_account(session, '5WX01234')

The ``get_balances`` function can be used to obtain information about the current buying power and cash balance:

.. code-block:: python

   balance = account.get_balances(session)
   print(balance)

>>> AccountBalance(account_number='5WX01234', cash_balance=Decimal('87.055'), long_equity_value=Decimal('4046.05'), short_equity_value=Decimal('0.0'), long_derivative_value=Decimal('0.0'), short_derivative_value=Decimal('0.0'), long_futures_value=Decimal('0.0'), short_futures_value=Decimal('0.0'), long_futures_derivative_value=Decimal('0.0'), short_futures_derivative_value=Decimal('0.0'), long_margineable_value=Decimal('0.0'), short_margineable_value=Decimal('0.0'), margin_equity=Decimal('4133.105'), equity_buying_power=Decimal('87.055'), derivative_buying_power=Decimal('87.055'), day_trading_buying_power=Decimal('0.0'), futures_margin_requirement=Decimal('0.0'), available_trading_funds=Decimal('0.0'), maintenance_requirement=Decimal('4048.85'), maintenance_call_value=Decimal('0.0'), reg_t_call_value=Decimal('0.0'), day_trading_call_value=Decimal('0.0'), day_equity_call_value=Decimal('0.0'), net_liquidating_value=Decimal('4133.105'), cash_available_to_withdraw=Decimal('87.06'), day_trade_excess=Decimal('87.06'), pending_cash=Decimal('0.0'), pending_cash_effect=<PriceEffect.NONE: 'None'>, long_cryptocurrency_value=Decimal('0.0'), short_cryptocurrency_value=Decimal('0.0'), cryptocurrency_margin_requirement=Decimal('0.0'), unsettled_cryptocurrency_fiat_amount=Decimal('0.0'), unsettled_cryptocurrency_fiat_effect=<PriceEffect.NONE: 'None'>, closed_loop_available_balance=Decimal('87.06'), equity_offering_margin_requirement=Decimal('0.0'), long_bond_value=Decimal('0.0'), bond_margin_requirement=Decimal('0.0'), snapshot_date=datetime.date(2023, 11, 28), reg_t_margin_requirement=Decimal('4048.85'), futures_overnight_margin_requirement=Decimal('0.0'), futures_intraday_margin_requirement=Decimal('0.0'), maintenance_excess=Decimal('87.055'), pending_margin_interest=Decimal('0.0'), effective_cryptocurrency_buying_power=Decimal('87.055'), updated_at=datetime.datetime(2023, 11, 28, 20, 54, 33, 556000, tzinfo=datetime.timezone.utc), apex_starting_day_margin_equity=None, buying_power_adjustment=None, buying_power_adjustment_effect=None, time_of_day=None)

To obtain information about current positions:

.. code-block:: python

   positions = account.get_positions(session)
   print(positions[0])

>>> CurrentPosition(account_number='5WX01234', symbol='BRK/B', instrument_type=<InstrumentType.EQUITY: 'Equity'>, underlying_symbol='BRK/B', quantity=Decimal('10'), quantity_direction='Long', close_price=Decimal('361.34'), average_open_price=Decimal('339.63'), multiplier=1, cost_effect='Credit', is_suppressed=False, is_frozen=False, realized_day_gain=Decimal('18.5'), realized_today=Decimal('279.15'), created_at=datetime.datetime(2023, 3, 31, 14, 35, 40, 138000, tzinfo=datetime.timezone.utc), updated_at=datetime.datetime(2023, 8, 10, 15, 42, 7, 482000, tzinfo=datetime.timezone.utc), mark=None, mark_price=None, restricted_quantity=Decimal('0'), expires_at=None, fixing_price=None, deliverable_type=None, average_yearly_market_close_price=Decimal('339.63'), average_daily_market_close_price=Decimal('361.34'), realized_day_gain_effect=<PriceEffect.CREDIT: 'Credit'>, realized_day_gain_date=datetime.date(2023, 8, 10), realized_today_effect=<PriceEffect.CREDIT: 'Credit'>, realized_today_date=datetime.date(2023, 8, 10))

TODO:
get_history
get_net_liquidating_value_history
get_live_orders
delete_order(and place and replace)
get_order_history

There are many more things you can do with an ``Account`` object--check out the SDK Reference section!