Sessions
========

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
To create a production (real) session using your normal login:

.. code-block:: python

   from tastytrade import ProductionSession
   session = ProductionSession('username', 'password')

A certification (test) account can be created `here <https://developer.tastytrade.com/sandbox/>`_, then used to create a session:

.. code-block:: python

   from tastytrade import CertificationSession
   session = CertificationSession('username', 'password')

You can make a session persistent by generating a remember token, which is valid for 24 hours:

.. code-block:: python

   session = ProductionSession('username', 'password', remember_me=True)
   remember_token = session.remember_token
   # remember token replaces the password for the next login
   new_session = ProductionSession('username', remember_token=remember_token)

Events
------

A ``ProductionSession`` can be used to make simple requests to the dxfeed REST API and pull quotes, greeks and more.
These requests are slower than ``DataStreamer`` and a separate request is required for each event fetched, so they're really more appropriate for a task that just needs to grab some information once. For recurring data feeds/streams or more time-sensitive tasks, the streamer is more appropriate.

Events are simply market data at a specific timestamp. There's a variety of different kinds of events supported, including:

- ``Candle``
  Information about open, high, low, and closing prices for an instrument during a certain time range
- ``Greeks``
  (options only) Black-Scholes variables for an option, like delta, gamma, and theta
- ``Quote``
  Live bid and ask prices for an instrument

Let's look at some examples for these three:

.. code-block:: python

   from tastytrade.dxfeed import EventType
   symbols = ['SPY', 'SPX']
   quotes = session.get_event(EventType.QUOTE, symbols)
   print(quotes)

>>> [Quote(eventSymbol='SPY', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='Q', bidPrice=411.58, bidSize=400.0, askTime=0, askExchangeCode='Q', askPrice=411.6, askSize=1313.0), Quote(eventSymbol='SPX', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='\x00', bidPrice=4122.49, bidSize='NaN', askTime=0, askExchangeCode='\x00', askPrice=4123.65, askSize='NaN')]

To fetch greeks, we need the option symbol in dxfeed format, which can be obtained using :meth:`get_option_chain`:

.. code-block:: python

   from tastytrade.instruments import get_option_chain
   from datetime import date

   chain = get_option_chain(session, 'SPLG')
   subs_list = [chain[date(2023, 6, 16)][0].streamer_symbol]
   greeks = session.get_event(EventType.GREEKS, subs_list)
   print(greeks)

>>> [Greeks(eventSymbol='.SPLG230616C23', eventTime=0, eventFlags=0, index=7235129486797176832, time=1684559855338, sequence=0, price=26.3380972233688, volatility=0.396983376650804, delta=0.999999999996191, gamma=4.81989763184255e-12, theta=-2.5212017514875e-12, rho=0.01834504287973133, vega=3.7003015672215e-12)]

Fetching candles requires a bit more info, like the candle width and the start time:

.. code-block:: python

   from datetime import datetime, timedelta

   subs_list = ['SPY']
   start_time = datetime.now() - timedelta(days=30)  # 1 month ago
   candles = session.get_candle(subs_list, interval='1d', start_time=start_time)
   print(candles[-3:])

>>> [Candle(eventSymbol='SPY{=d}', eventTime=0, eventFlags=0, index=7254715159019520000, time=1689120000000, sequence=0, count=142679, open=446.39, high=447.4799, low=444.91, close=446.02, volume=91924527, vwap=445.258750197419, bidVolume=14787054, askVolume=15196448, impVolatility='NaN', openInterest='NaN'), Candle(eventSymbol='SPY{=d}', eventTime=0, eventFlags=0, index=7255086244193894400, time=1689206400000, sequence=0, count=106759, open=447.9, high=450.38, low=447.45, close=449.56, volume=72425241, vwap=448.163832976481, bidVolume=10384321, askVolume=11120400, impVolatility='NaN', openInterest='NaN'), Candle(eventSymbol='SPY{=d}', eventTime=0, eventFlags=0, index=7255457329368268800, time=1689292800000, sequence=0, count=113369, open=450.475, high=451.36, low=448.49, close=449.28, volume=69815823, vwap=449.948156765549, bidVolume=10905920, askVolume=13136337, impVolatility='NaN', openInterest='NaN')]
