Orders
======

Placing an order
----------------

.. code-block:: python

   from decimal import Decimal
   from tastytrade import Account
   from tastytrade.instruments import Equity
   from tastytrade.order import *

   account = Account.get_account(session, '5WX01234')
   symbol = Equity.get_equity(session, 'USO')
   leg = symbol.build_leg(Decimal('5'), OrderAction.BUY_TO_OPEN)  # buy to open 5 shares

   order = NewOrder(
       time_in_force=OrderTimeInForce.DAY,
       order_type=OrderType.LIMIT,
       legs=[leg],  # you can have multiple legs in an order
       price=Decimal('-10')  # limit price, $10/share debit for a total value of $50
   )
   response = account.place_order(session, order, dry_run=True)  # a test order
   print(response)

>>> PlacedOrderResponse(buying_power_effect=BuyingPowerEffect(change_in_margin_requirement=Decimal('125.0'), change_in_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, change_in_buying_power=Decimal('125.004'), change_in_buying_power_effect=<PriceEffect.DEBIT: 'Debit'>, current_buying_power=Decimal('1000.0'), current_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, new_buying_power=Decimal('874.996'), new_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, isolated_order_margin_requirement=Decimal('125.0'), isolated_order_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, is_spread=False, impact=Decimal('125.004'), effect=<PriceEffect.DEBIT: 'Debit'>), fee_calculation=FeeCalculation(regulatory_fees=Decimal('0.0'), regulatory_fees_effect=<PriceEffect.NONE: 'None'>, clearing_fees=Decimal('0.004'), clearing_fees_effect=<PriceEffect.DEBIT: 'Debit'>, commission=Decimal('0.0'), commission_effect=<PriceEffect.NONE: 'None'>, proprietary_index_option_fees=Decimal('0.0'), proprietary_index_option_fees_effect=<PriceEffect.NONE: 'None'>, total_fees=Decimal('0.004'), total_fees_effect=<PriceEffect.DEBIT: 'Debit'>), order=PlacedOrder(account_number='5WV69754', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, size='5', underlying_symbol='USO', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.RECEIVED: 'Received'>, cancellable=True, editable=True, edited=False, updated_at=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='USO', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('5'), remaining_quantity=Decimal('5'), fills=[])], id=None, price=Decimal('50.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=None, cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=None, reject_reason=None, user_id=None, username=None, terminal_at=None, complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), complex_order=None, warnings=[Message(code='tif_next_valid_sesssion', message='Your order will begin working during next valid session.', preflight_id=None)], errors=None)

Notice the use of the ``dry_run`` parameter in the call to ``place_order``. This is used to calculate the effects that an order would have on the account's buying power and the fees that would be charged without actually placing the order. This is typically used to provide an order confirmation screen before sending the order.
To send the order, pass ``dry_run=False``, and the response will be populated with a ``PlacedOrderResponse``, which contains information about the order and account.
Also, rather than using an explicit credit/debit toggle like the Tastytrade platform, the SDK simply assumes negative numbers are debits and positive ones are credits.

Managing orders
---------------

Once we've placed an order, it's often necessary to modify or cancel the order for a variety of reasons. Thankfully, this is easy and handled through the ``Account`` object:

.. code-block:: python

   previous_order.price = Decimal('-10.05')  # let's pay more to get a fill!
   response = account.replace_order(session, previous_response.order.id, previous_order)

Cancelling an order is similar:

.. code-block:: python

   account.delete_order(session, placed_order.id)

Placed orders are assigned a status, like "Received", "Cancelled", or "Filled". To watch for status changes in real time, you can use the :doc:`Account Streamer <account-streamer>`.
To get current order status, you can just call ``get_live_orders``. (The name is somewhat misleading! It returns not only live orders, but also cancelled and filled ones over the past 24 hours.)

.. code-block:: python

   orders = account.get_live_orders(session)
   print(orders)

>>> [PlacedOrder(account_number='5WX01234', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, underlying_symbol='SPY', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.CANCELLED: 'Cancelled'>, cancellable=False, editable=False, edited=False, updated_at=datetime.datetime(2024, 2, 6, 0, 2, 56, 559000, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='SPY', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('1'), remaining_quantity=Decimal('1'), fills=[])], size='1', id='306731648', price=Decimal('40.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=datetime.datetime(2024, 2, 6, 0, 2, 56, 548000, tzinfo=datetime.timezone.utc), cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=datetime.datetime(2024, 2, 6, 0, 2, 55, 347000, tzinfo=datetime.timezone.utc), reject_reason=None, user_id=None, username=None, terminal_at=datetime.datetime(2024, 2, 6, 0, 2, 56, 548000, tzinfo=datetime.timezone.utc), complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), PlacedOrder(account_number='5WX01234', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, underlying_symbol='SPY', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.CANCELLED: 'Cancelled'>, cancellable=False, editable=False, edited=True, updated_at=datetime.datetime(2024, 2, 6, 0, 2, 55, 362000, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='SPY', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('1'), remaining_quantity=Decimal('1'), fills=[])], size='1', id='306731647', price=Decimal('42.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=datetime.datetime(2024, 2, 6, 0, 2, 55, 341000, tzinfo=datetime.timezone.utc), cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=datetime.datetime(2024, 2, 6, 0, 2, 54, 781000, tzinfo=datetime.timezone.utc), reject_reason=None, user_id=None, username=None, terminal_at=datetime.datetime(2024, 2, 6, 0, 2, 55, 341000, tzinfo=datetime.timezone.utc), complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), PlacedOrder(account_number='5WX01234', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, underlying_symbol='SPY', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.CANCELLED: 'Cancelled'>, cancellable=False, editable=False, edited=False, updated_at=datetime.datetime(2024, 2, 6, 0, 2, 54, 433000, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='SPY', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('1'), remaining_quantity=Decimal('1'), fills=[])], size='1', id='306731645', price=Decimal('42.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=datetime.datetime(2024, 2, 6, 0, 2, 54, 422000, tzinfo=datetime.timezone.utc), cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=datetime.datetime(2024, 2, 6, 0, 2, 53, 203000, tzinfo=datetime.timezone.utc), reject_reason=None, user_id=None, username=None, terminal_at=datetime.datetime(2024, 2, 6, 0, 2, 54, 422000, tzinfo=datetime.timezone.utc), complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), PlacedOrder(account_number='5WX01234', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, underlying_symbol='SPY', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.CANCELLED: 'Cancelled'>, cancellable=False, editable=False, edited=False, updated_at=datetime.datetime(2024, 2, 5, 23, 46, 44, 844000, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='SPY', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('1'), remaining_quantity=Decimal('1'), fills=[])], size='1', id='306731381', price=Decimal('40.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=datetime.datetime(2024, 2, 5, 23, 46, 44, 833000, tzinfo=datetime.timezone.utc), cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=datetime.datetime(2024, 2, 5, 23, 46, 43, 150000, tzinfo=datetime.timezone.utc), reject_reason=None, user_id=None, username=None, terminal_at=datetime.datetime(2024, 2, 5, 23, 46, 44, 833000, tzinfo=datetime.timezone.utc), complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), PlacedOrder(account_number='5WX01234', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, underlying_symbol='SPY', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.CANCELLED: 'Cancelled'>, cancellable=False, editable=False, edited=True, updated_at=datetime.datetime(2024, 2, 5, 23, 46, 43, 183000, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='SPY', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('1'), remaining_quantity=Decimal('1'), fills=[])], size='1', id='306731380', price=Decimal('42.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=datetime.datetime(2024, 2, 5, 23, 46, 43, 145000, tzinfo=datetime.timezone.utc), cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=datetime.datetime(2024, 2, 5, 23, 46, 41, 647000, tzinfo=datetime.timezone.utc), reject_reason=None, user_id=None, username=None, terminal_at=datetime.datetime(2024, 2, 5, 23, 46, 43, 145000, tzinfo=datetime.timezone.utc), complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None)]

For less recent orders, we can get the full order history with ``get_order_history``.

Complex Orders
--------------

Tastytrade supports two kinds of complex orders, "OCO" and "OTOCO", which are explained `here <https://support.tastyworks.com/support/solutions/articles/43000544221-bracket-orders>`_.

To create an OTOCO order, you need an entry point order, a stop loss order, and a profit-taking order:

.. code-block:: python

   from decimal import Decimal
   from tastytrade.instruments import Equity
   from tastytrade.order import *

   symbol = Equity.get_equity(session, 'AAPL')
   opening = symbol.build_leg(Decimal(1), OrderAction.BUY_TO_OPEN) # buy to open 1 share
   closing = symbol.build_leg(Decimal(1), OrderAction.SELL_TO_CLOSE) # sell to close 1 share

   otoco = NewComplexOrder(
       trigger_order=NewOrder(
           time_in_force=OrderTimeInForce.DAY,
           order_type=OrderType.LIMIT,
           legs=[opening],
           price=Decimal('-180')  # open for $180 debit
       ),
       orders=[
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.LIMIT,
               legs=[closing],
               price=Decimal('200')  # take profits
           ),
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.STOP,
               legs=[closing],
               stop_trigger=Decimal('160')  # stop loss
           )
       ]
   )
   resp = account.place_complex_order(session, otoco, dry_run=False)

An OCO order is similar, but has no trigger order. It's used to add a profit-taking and a stop loss order to an existing position. Here's an example, assuming the account already has an open position of 10 long shares of SPY:

.. code-block:: python

   symbol = Equity.get_equity(session, 'SPY')
   closing = symbol.build_leg(Decimal(10), OrderAction.SELL_TO_CLOSE) # sell to close 10 shares

   oco = NewComplexOrder(
       orders=[
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.LIMIT,
               legs=[closing],
               price=Decimal('4800'),  # take profits
               price_effect=PriceEffect.CREDIT
           ),
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.STOP,
               legs=[closing],
               stop_trigger=Decimal('4000'),  # stop loss
               price_effect=PriceEffect.CREDIT
           )
       ]
   )
   resp = account.place_complex_order(session, oco, dry_run=False)

Note that to cancel complex orders, you need to use the ``delete_complex_order`` function, NOT ``delete_order``.
