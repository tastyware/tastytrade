Instruments
===========

In the Tastytrade API, an instrument is a tradeable object, such as a cryptocurrency, an option, an equity/ETF, futures, futures options, and warrants.
The SDK makes it easy to fetch, trade, and perform various other operations for these instruments.

Initialization
--------------

Instruments follow a basic schema for initialization. To create an instrument(s), use the classmethods for the desired type of instrument:

- ``Cryptocurrency.get_cryptocurrency()``, ``Cryptocurrency.get_cryptocurrencies()``
- ``Equity.get_equity()``, ``Equity.get_equities()``
- ``Future.get_future()``, ``Future.get_futures()``
- ``Option.get_option()``, ``Option.get_options()``
- ``FutureOption.get_future_option()``, ``FutureOption.get_future_options()``

These functions take the session object as the first parameter, and the symbol (or list of symbols) as the second.
Note that ETFs and indices are treated as equities for the purposes of the API.

.. code-block:: python

   from tastytrade.instruments import Equity, FutureOption

   equities = Equity.get_equities(session, ['SPY', 'AAPL'])
   print(equities[0].is_etf, equities[0].description)
   future_option = FutureOption.get_future_option(session, './GCJ4 OG4G4 240223P1915')
   print(future_option.exchange)

>>> (False, 'APPLE INC')
>>> 'CME'

The different instruments have a host of properties that will be automatically populated with their associated values upon initialization. You can explore these properties in depth in the "SDK Reference" section.

Options chains
--------------

The symbol structure for options and futures options is somewhat complex, so you can use ``get_option_chain()`` and ``get_future_option_chain()`` to get the instruments for a specific underlying as explained below.

.. code-block:: python

   from tastytrade.instruments import get_option_chain, get_future_option_chain
   from tastytrade.utils import get_tasty_monthly

   chain = get_option_chain(session, 'SPLG')
   exp = get_tasty_monthly()  # 45 DTE expiration!
   print(chain[exp][0])
   future_chain = get_future_option_chain(session, '/MCL')
   print(future_chain.keys())  # print all expirations

>>> instrument_type=<InstrumentType.EQUITY_OPTION: 'Equity Option'> symbol='SPLG  240315C00024000' active=True strike_price=Decimal('24.0') root_symbol='SPLG' underlying_symbol='SPLG' expiration_date=datetime.date(2024, 3, 15) exercise_style='American' shares_per_contract=100 option_type=<OptionType.CALL: 'C'> option_chain_type='Standard' expiration_type='Regular' settlement_type='PM' stops_trading_at=datetime.datetime(2024, 3, 15, 20, 0, tzinfo=datetime.timezone.utc) market_time_instrument_collection='Equity Option' days_to_expiration=38 expires_at=datetime.datetime(2024, 3, 15, 20, 0, tzinfo=datetime.timezone.utc) is_closing_only=False listed_market=None halted_at=None old_security_number=None streamer_symbol='.SPLG240315C24'
>>> dict_keys([datetime.date(2024, 7, 17), datetime.date(2024, 6, 14), datetime.date(2024, 9, 17), datetime.date(2024, 11, 15), datetime.date(2024, 12, 16), datetime.date(2024, 2, 9), datetime.date(2024, 5, 16), datetime.date(2025, 1, 15), datetime.date(2024, 8, 15), datetime.date(2024, 2, 16), datetime.date(2024, 2, 14), datetime.date(2024, 10, 17), datetime.date(2024, 4, 17), datetime.date(2024, 3, 15)])

Alternatively, ``NestedOptionChain`` and ``NestedFutureOptionChain`` provide a structured way to fetch chain expirations and available strikes.

.. code-block:: python

   from tastytrade.instruments import NestedOptionChain

   chain = NestedOptionChain.get_chain(session, 'SPY')
   print(chain.expirations[0].strikes[0])

>>> Strike(strike_price=Decimal('437.0'), call='SPY   240417C00437000', put='SPY   240417P00437000', call_streamer_symbol='.SPY240417C437', put_streamer_symbol='.SPY240417P437')

Each expiration contains a list of these strikes, which have the associated put and call symbols that can then be used to fetch option objects via ``Option.get_options()`` or converted to dxfeed symbols for use with the streamer via ``Option.occ_to_streamer_symbol()``.

Placing trades
--------------

Probably the most powerful tool available for instruments is the ``build_leg()`` function. This allows an instrument to be quickly converted into a tradeable 'leg', which by itself or together with other legs forms the basis for a trade.
This makes placing new trades across a wide variety of instruments surprisingly simple:

.. code-block:: python

   from tastytrade.instruments import get_future_option_chain
   from tastytrade.order import *
   from datetime import date

   chain = get_future_option_chain(session, '/MCL')
   put = chain[date(2024, 3, 15)][286]
   call = chain[date(2024, 3, 15)][187]

   order = NewOrder(
       time_in_force=OrderTimeInForce.DAY,
       order_type=OrderType.LIMIT,
       legs=[
           # two parameters: quantity and order action
           put.build_leg(Decimal(1), OrderAction.SELL_TO_OPEN),
           call.build_leg(Decimal(1), OrderAction.SELL_TO_OPEN)
       ],
       price=Decimal('1.25')  # price is always per quantity, not total
   )
   # assuming an initialized account
   account.place_order(session, order, dry_run=False)

That's it! We just sold a micro crude oil futures strangle in a few lines of code.
Note that price is per quantity, not the price for the entire order! So if the legs looked like this:

.. code-block:: python

   legs=[
       put.build_leg(Decimal(2), OrderAction.SELL_TO_OPEN),
       call.build_leg(Decimal(2), OrderAction.SELL_TO_OPEN)
   ]

the price would still be ``Decimal('1.25')``, and the total credit collected would be $2.50. This holds true for ratio spreads, so a 4:2 ratio spread should be priced as a 2:1 ratio spread.
