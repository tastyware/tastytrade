Account Streamer
================

Basic usage
-----------

The account streamer is used to track account-level updates, such as order fills, watchlist updates and quote alerts.
Typically, you'll want a separate task running for the account streamer, which can then notify your application about important events.

Here's an example of setting up an account streamer to continuously wait for events and print them:

.. code-block:: python

    from tastytrade import Account, AlertStreamer, Watchlist

    async with AlertStreamer(session) as streamer:
        accounts = Account.get_accounts(session)

        # updates to balances, orders, and positions
        await streamer.subscribe_accounts(accounts)
        # changes in public watchlists
        await streamer.subscribe_public_watchlists()
        # quote alerts configured by the user
        await streamer.subscribe_quote_alerts()

        async for wl in streamer.listen(Watchlist):
            print(wl)

Probably the most important information the account streamer handles is order fills. We can listen just for orders like so:

.. code-block:: python

    from tastytrade.order import PlacedOrder

    async with AlertStreamer(session) as streamer:
        accounts = Account.get_accounts(session)
        await streamer.subscribe_accounts(accounts)

        async for order in streamer.listen(PlacedOrder):
            print(order)

Retry callback
--------------

The account streamer has a special "callback" function which can be used to execute arbitrary code whenever the websocket reconnects. This is useful for re-subscribing to whatever alerts you wanted to subscribe to initially (in fact, you can probably use the same function/code you use when initializing the connection).
The callback function should look something like this:

.. code-block:: python

    async def callback(streamer: AlertStreamer, arg1, arg2):
        await streamer.subscribe_quote_alerts()

The requirements are that the first parameter be the `AlertStreamer` instance, and the function should be asynchronous. Other than that, you have the flexibility to decide what arguments you want to use.
This callback can then be used when creating the streamer:

.. code-block:: python

    async with AlertStreamer(session, reconnect_fn=callback, reconnect_args=(arg1, arg2)) as streamer:
        # ...

The reconnection uses `websockets`' exponential backoff algorithm, which can be configured through environment variables `here <https://websockets.readthedocs.io/en/14.1/reference/variables.html>`_.
