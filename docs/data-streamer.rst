Data Streamer
=============

Basic usage
-----------

The streamer is a websocket connection to dxfeed (the Tastytrade data provider) that allows you to subscribe to real-time data for quotes, greeks, and more.
You can create a streamer using an active production session:

.. code-block:: python

   from tastytrade import DXLinkStreamer
   async with DXLinkStreamer(session) as streamer:
       pass

Once you've created the streamer, you can subscribe/unsubscribe to events, like ``Quote``:

.. code-block:: python

   from tastytrade.dxfeed import Quote
   subs_list = ['SPY']  # you can add more symbols here!

   async with DXLinkStreamer(session) as streamer:
       await streamer.subscribe(Quote, subs_list)
       quotes = {}
       async for quote in streamer.listen(Quote):
           quotes[quote.event_symbol] = quote
           if len(quotes) >= len(subs_list):
               break
       print(quotes)

>>> [{'SPY': Quote(event_symbol='SPY', event_time=0, sequence=0, time_nano_part=0, bid_time=0, bid_exchange_code='Q', bid_price=411.58, bid_size=400.0, ask_time=0, ask_exchange_code='Q', ask_price=411.6, ask_size=1313.0), 'SPX': Quote(event_symbol='SPX', event_time=0, sequence=0, time_nano_part=0, bid_time=0, bid_exchange_code='\x00', bid_price=4122.49, bid_size='NaN', ask_time=0, ask_exchange_code='\x00', ask_price=4123.65, ask_size='NaN')}]

We can also use the streamer to stream greeks for options symbols:

.. code-block:: python

   from tastytrade.dxfeed import Greeks
   from tastytrade.instruments import get_option_chain
   from tastytrade.utils import get_tasty_monthly

   chain = await get_option_chain(session, 'SPLG')
   exp = get_tasty_monthly()  # 45 DTE expiration!
   subs_list = [chain[exp][0].streamer_symbol]

   async with DXLinkStreamer(session) as streamer:
       await streamer.subscribe(Greeks, subs_list)
       greeks = await streamer.get_event(Greeks)
       print(greeks)

>>> Greeks(event_symbol='.SPLG230616C23', event_time=0, event_flags=0, index=7235129486797176832, time=1684559855338, sequence=0, price=26.3380972233688, volatility=0.396983376650804, delta=0.999999999996191, gamma=4.81989763184255e-12, theta=-2.5212017514875e-12, rho=0.01834504287973133, vega=3.7003015672215e-12)

Auto-retries
------------

Often, streamer connections should be long-lived and persistent. While the SDK doesn't provide this functionality itself, it's pretty trivial to build with just a few lines of code:

.. code-block:: python

    from anyio import sleep
    from httpx_ws import HTTPXWSException

    tries, max_tries = 0, 3
    while (tries := tries + 1) <= max_tries:
        try:
            async with DXLinkStreamer(session) as streamer:
                print("Yay! Connected!")
                ...
        except* HTTPXWSException:
            print("Oh no! Disconnected!")
            await sleep(tries ** 2)

Now we have persistence, exponential backoff, and disconnect/reconnect hooks--easy!
