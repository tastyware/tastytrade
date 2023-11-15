Data Streamer
=============

Basic usage
-----------

The streamer is a websocket connection to dxfeed (the Tastytrade data provider) that allows you to subscribe to real-time data for quotes, greeks, and more.
You can create a streamer using an active production session:

.. code-block:: python

   from tastytrade import DXFeedStreamer
   streamer = await DXFeedStreamer.create(session)

Once you've created the streamer, you can subscribe/unsubscribe to events, like ``Quote``:

.. code-block:: python

   from tastytrade.dxfeed import EventType
   subs_list = ['SPY', 'SPX']

   await streamer.subscribe(EventType.QUOTE, subs_list)
   quotes = []
   async for quote in streamer.listen(EventType.QUOTE):
      quotes.append(quote)
      if len(quotes) >= len(subs_list):
         break
   print(quotes)

>>> [Quote(eventSymbol='SPY', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='Q', bidPrice=411.58, bidSize=400.0, askTime=0, askExchangeCode='Q', askPrice=411.6, askSize=1313.0), Quote(eventSymbol='SPX', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='\x00', bidPrice=4122.49, bidSize='NaN', askTime=0, askExchangeCode='\x00', askPrice=4123.65, askSize='NaN')]

We can also use the streamer to stream greeks for options symbols:

.. code-block:: python

   from tastytrade.instruments import get_option_chain
   from datetime import date

   chain = get_option_chain(session, 'SPLG')
   subs_list = [chain[date(2023, 6, 16)][0].streamer_symbol]

   await streamer.subscribe(EventType.GREEKS, subs_list)
   greeks = []
   async for greek in streamer.listen(EventType.GREEKS):
      greeks.append(greek)
      if len(greeks) >= len(subs_list):
         break
   print(greeks)

>>> [Greeks(eventSymbol='.SPLG230616C23', eventTime=0, eventFlags=0, index=7235129486797176832, time=1684559855338, sequence=0, price=26.3380972233688, volatility=0.396983376650804, delta=0.999999999996191, gamma=4.81989763184255e-12, theta=-2.5212017514875e-12, rho=0.01834504287973133, vega=3.7003015672215e-12)]

Advanced usage
--------------

Since the streamer makes use of Python's ``asyncio`` library, it's not always straightforward to use; however, it's very powerful.
For example, we can use the streamer to create an option chain that will continuously update prices as new data arrives:

.. code-block:: python

   import asyncio
   from datetime import date
   from dataclasses import dataclass
   from tastytrade.instruments import get_option_chain
   from tastytrade.dxfeed import Greeks, Quote

   @dataclass
   class LivePrices:
      quotes: dict[str, Quote]
      greeks: dict[str, Greeks]
      streamer: DXFeedStreamer
      puts: list[Option]
      calls: list[Option]

      @classmethod
      async def create(
         cls,
         session: ProductionSession,
         symbol: str = 'SPY',
         expiration: date = date.today()
      ):
         chain = get_option_chain(session, symbol)
         options = [o for o in chain[expiration]]
         # the `streamer_symbol` property is the symbol used by the streamer
         streamer_symbols = [o.streamer_symbol for o in options]

         streamer = await DXFeedStreamer.create(session)
         # subscribe to quotes and greeks for all options on that date
         await streamer.subscribe(EventType.QUOTE, [symbol] + streamer_symbols)
         await streamer.subscribe(EventType.GREEKS, streamer_symbols)
         
         puts = [o for o in options if o.option_type == OptionType.PUT]
         calls = [o for o in options if o.option_type == OptionType.CALL]
         self = cls({}, {}, streamer, puts, calls)

         t_listen_greeks = asyncio.create_task(self._update_greeks())
         t_listen_quotes = asyncio.create_task(self._update_quotes())
         asyncio.gather(t_listen_greeks, t_listen_quotes)

         # wait we have quotes and greeks for each option
         while len(self.greeks) != len(options) or len(self.quotes) != len(options):
            await asyncio.sleep(0.1)

         return self

      async def _update_greeks(self):
         async for e in self.streamer.listen(EventType.GREEKS):
            self.greeks[e.eventSymbol] = e
      
      async def _update_quotes(self):
         async for e in self.streamer.listen(EventType.QUOTE):
            self.quotes[e.eventSymbol] = e

Now, we can access the quotes and greeks at any time, and they'll be up-to-date with the live prices from the streamer:

.. code-block:: python

   live_prices = await LivePrices.create(session, 'SPY', date(2023, 7, 21))
   symbol = live_prices.calls[44].streamer_symbol
   print(live_prices.quotes[symbol], live_prices.greeks[symbol])

>>> Quote(eventSymbol='.SPY230721C387', eventTime=0, sequence=0, timeNanoPart=0, bidTime=1689365699000, bidExchangeCode='X', bidPrice=62.01, bidSize=50.0, askTime=1689365699000, askExchangeCode='X', askPrice=62.83, askSize=50.0) Greeks(eventSymbol='.SPY230721C387', eventTime=0, eventFlags=0, index=7255910303911641088, time=1689398266363, sequence=0, price=62.6049270064687, volatility=0.536152815048564, delta=0.971506591907638, gamma=0.001814464566110275, theta=-0.1440768557397271, rho=0.0831882577866199, vega=0.0436861878838861)
