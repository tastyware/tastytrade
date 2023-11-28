Orders
======

Placing an order
----------------

.. code-block:: python

   from decimal import Decimal
   from tastytrade import Account
   from tastytrade.instruments import Equity
   from tastytrade.order import *

   account = Account.get_account(session, '5WV69754')
   symbol = Equity.get_equity(session, 'USO')
   leg = symbol.build_leg(Decimal('5'), OrderAction.BUY_TO_OPEN)  # buy to open 5 shares

   order = NewOrder(
       time_in_force=OrderTimeInForce.DAY,
       order_type=OrderType.LIMIT,
       legs=[leg],  # you can have multiple legs in an order
       price=Decimal('50'),  # limit price, here $50 for 5 shares = $10/share
       price_effect=PriceEffect.DEBIT
   )
   response = account.place_order(session, order, dry_run=True)  # a test order
   print(response)

>>> PlacedOrderResponse(buying_power_effect=BuyingPowerEffect(change_in_margin_requirement=Decimal('125.0'), change_in_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, change_in_buying_power=Decimal('125.004'), change_in_buying_power_effect=<PriceEffect.DEBIT: 'Debit'>, current_buying_power=Decimal('1000.0'), current_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, new_buying_power=Decimal('874.996'), new_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, isolated_order_margin_requirement=Decimal('125.0'), isolated_order_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, is_spread=False, impact=Decimal('125.004'), effect=<PriceEffect.DEBIT: 'Debit'>), fee_calculation=FeeCalculation(regulatory_fees=Decimal('0.0'), regulatory_fees_effect=<PriceEffect.NONE: 'None'>, clearing_fees=Decimal('0.004'), clearing_fees_effect=<PriceEffect.DEBIT: 'Debit'>, commission=Decimal('0.0'), commission_effect=<PriceEffect.NONE: 'None'>, proprietary_index_option_fees=Decimal('0.0'), proprietary_index_option_fees_effect=<PriceEffect.NONE: 'None'>, total_fees=Decimal('0.004'), total_fees_effect=<PriceEffect.DEBIT: 'Debit'>), order=PlacedOrder(account_number='5WV69754', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, size='5', underlying_symbol='USO', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.RECEIVED: 'Received'>, cancellable=True, editable=True, edited=False, updated_at=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='USO', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('5'), remaining_quantity=Decimal('5'), fills=[])], id=None, price=Decimal('50.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=None, cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=None, reject_reason=None, user_id=None, username=None, terminal_at=None, complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), complex_order=None, warnings=[Message(code='tif_next_valid_sesssion', message='Your order will begin working during next valid session.', preflight_id=None)], errors=None)

Notice the use of the ``dry_run`` parameter in the call to ``place_order``. This is used to calculate the effects that an order would have on the account's buying power and the fees that would be charged without actually placing the order. This is typically used to provide an order confirmation screen before sending the order.
To send the order, pass ``dry_run=False``, and the response will be populated with a ``PlacedOrderResponse``, which contains information about the order and account.

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
           price=Decimal('180'),
           price_effect=PriceEffect.DEBIT
       ),
       orders=[
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.LIMIT,
               legs=[closing],
               price=Decimal('200'),  # take profits
               price_effect=PriceEffect.CREDIT
           ),
           NewOrder(
               time_in_force=OrderTimeInForce.GTC,
               order_type=OrderType.STOP,
               legs=[closing],
               stop_trigger=Decimal('160'),  # stop loss
               price_effect=PriceEffect.CREDIT
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
