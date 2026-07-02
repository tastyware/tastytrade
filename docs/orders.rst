Orders
======

Placing an order
----------------

.. code-block:: python

   from decimal import Decimal
   from tastytrade import Account
   from tastytrade.instruments import Equity
   from tastytrade.order import *

   account = await Account.get(session, '5WX01234')
   symbol = await Equity.get(session, 'USO')
   leg = symbol.build_leg(5, OrderAction.BUY_TO_OPEN)  # buy to open 5 shares

   order = LimitOrder(
       legs=[leg],  # you can have multiple legs in an order
       price=Decimal('-10')  # limit price, $10/share debit for a total value of $50
   )
   response = await account.place_order(session, order, dry_run=True)  # a test order
   print(response)

>>> buying_power_effect=BuyingPowerEffect(change_in_margin_requirement=Decimal('-50.0') change_in_buying_power=Decimal('-50.004') current_buying_power=Decimal('190.95') new_buying_power=Decimal('140.946') isolated_order_margin_requirement=Decimal('-50.0') impact=Decimal('50.004') effect=<PriceEffect.DEBIT: 'Debit'>) order=UnplacedOrder(account_number='5WX01234' time_in_force=<OrderTimeInForce.DAY: 'Day'> order_type=<OrderType.LIMIT: 'Limit'> underlying_symbol='USO' underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'> status=<OrderStatus.RECEIVED: 'Received'> cancellable=True editable=True updated_at=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=TzInfo(0)) legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'> symbol='USO' action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'> quantity=5 remaining_quantity=Decimal('5'))] size=Decimal('5') price=Decimal('-10.0') source='tastyware/tastytrade:v13.0.0') fee_calculation=FeeCalculation(clearing_fees=Decimal('-0.004') total_fees=Decimal('-0.004'))

Notice the use of the ``dry_run`` parameter in the call to ``place_order``. This is used to calculate the effects that an order would have on the account's buying power and the fees that would be charged without actually placing the order. This is typically used to provide an order confirmation screen before sending the order.
To send the order, pass ``dry_run=False``, and the response will be populated with information about the order and account.

.. important::
   Rather than using an explicit credit/debit toggle like the Tastytrade platform, the SDK simply assumes negative numbers are debits and positive ones are credits.

Managing orders
---------------

Once we've placed an order, it's often necessary to modify or cancel the order for a variety of reasons. Thankfully, this is easy and handled through the :class:`~tastytrade.account.Account` object:

.. code-block:: python

   previous_order.price -= Decimal('0.05')  # let's pay more to get a fill!
   replaced_order = await account.replace_order(session, previous_response.order.id, previous_order)

Cancelling an order is similar:

.. code-block:: python

   await account.delete_order(session, placed_order.id)

Placed orders are assigned a status, like "Received", "Cancelled", or "Filled". To watch for status changes in real time, you can use the :doc:`Account Streamer <account-streamer>`.
To get current order status, you can just call ``get_live_orders``. (The name is somewhat misleading! It returns not only live orders, but also cancelled and filled ones over the past 24 hours.)

.. code-block:: python

   orders = await account.get_live_orders(session)
   print(orders)

For less recent orders, we can get the full order history with ``get_order_history``.

Complex Orders
--------------

Tastytrade supports three kinds of complex orders, "OCO", "OTO", and "OTOCO", which are explained `here <https://support.tastyworks.com/support/solutions/articles/43000544221-bracket-orders>`_.

To create an OTOCO order, you need an entry point order, a stop loss order, and a profit-taking order:

.. code-block:: python

   from decimal import Decimal
   from tastytrade.instruments import Equity
   from tastytrade.order import *

   symbol = await Equity.get(session, 'AAPL')
   opening = symbol.build_leg(1, OrderAction.BUY_TO_OPEN) # buy to open 1 share
   closing = symbol.build_leg(1, OrderAction.SELL_TO_CLOSE) # sell to close 1 share

   otoco = OTOCOOrder(
       trigger_order=LimitOrder(
           legs=[opening], price=Decimal('-180')  # open for $180 debit
       ),
       take_profit=LimitOrder(
           time_in_force=OrderTimeInForce.GTC,
           legs=[closing],
           price=Decimal('200'),
       ),
       stop_loss=StopOrder(
           time_in_force=OrderTimeInForce.GTC,
           legs=[closing],
           stop_trigger=Decimal('160'),
       ),
   )
   res = await account.place_complex_order(session, otoco)

An OCO order is similar, but has no trigger order. It's used to add a profit-taking and a stop loss order to an existing position. Here's an example, assuming the account already has an open position of 10 long shares of SPY:

.. code-block:: python

   symbol = await Equity.get(session, 'SPY')
   closing = symbol.build_leg(10, OrderAction.SELL_TO_CLOSE) # sell to close 10 shares

   oco = OCOOrder(
       take_profit=LimitOrder(
           time_in_force=OrderTimeInForce.GTC,
           legs=[closing],
           price=Decimal('4800'),
       ),
       stop_loss=StopLimitOrder(
           time_in_force=OrderTimeInForce.GTC,
           legs=[closing],
           stop_trigger=Decimal('4000'),
           price=Decimal('3990'),
       ),
   )
   res = await account.place_complex_order(session, oco)

Note that to cancel entire complex orders, you need to use the ``delete_complex_order`` function, NOT ``delete_order`` (though you can use ``delete_order`` to delete individual components of a complex order).

An OTO order uses a trigger order as an entry point to create one or more orders:

.. code-block:: python

   oto = OTOOrder(
       trigger_order=LimitOrder(
           legs=[opening],
           price=Decimal('-4000'),
       ),
       orders=[
           LimitOrder(  # take profit order
               time_in_force=OrderTimeInForce.GTC,
               legs=[closing],
               price=Decimal('4800'),
           )
       ],
   )
   res = await account.place_complex_order(session, oto)

Market orders
-------------

Market orders are different as you let the market determine the price:

.. code-block:: python

    from tastytrade.order import MarketOrder

    symbol = await Equity.get(session, 'AAPL')
    order = MarketOrder(
        legs=[  # buy 1 share at market price
            symbol.build_leg(1, OrderAction.BUY_TO_OPEN),
        ]
    )
    await account.place_order(session, order, dry_run=True)

Notional orders are slightly different. Since the market will determine both the quantity and the price for you, you need to pass ``value`` instead of price, and pass ``None`` for the ``quantity`` parameter to ``build_leg``.

.. code-block:: python

    from tastytrade.order import NotionalOrder

    symbol = await Equity.get(session, 'AAPL')
    order = NotionalOrder(
        value=Decimal(-10),  # $10 debit, this will result in fractional shares
        legs=[
            symbol.build_leg(None, OrderAction.BUY_TO_OPEN),
        ]
    )
    await account.place_order(session, order, dry_run=True)

Cryptocurrency market orders
----------------------------

Cryptocurrency market orders should use the special ``IOC`` TIF:

.. code-block:: python

    from tastytrade.order import (
        InstrumentType,
        Leg,
        NotionalOrder,
        OrderAction,
        OrderTimeInForce,
    )

    order = NotionalOrder(
        time_in_force=OrderTimeInForce.IOC,
        value=-Decimal(100),  # buy $100 of ETH
        legs=[
            Leg(
                instrument_type=InstrumentType.CRYPTOCURRENCY,
                action=OrderAction.BUY_TO_OPEN,
                symbol="ETH/USD",
            ),
        ],
    )
