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
        # updates to balances, orders, and positions
        accounts = await Account.get(session)
        await streamer.subscribe_accounts(accounts)

        async for order in streamer.listen(PlacedOrder):
            print(order)

Auto-retries
------------

Often, account streamer connections should be long-lived and persistent. While the SDK doesn't provide this functionality itself, it's pretty trivial to build with just a few lines of code:

.. code-block:: python

    from anyio import sleep
    from httpx_ws import HTTPXWSException

    tries, max_tries = 0, 3
    while (tries := tries + 1) <= max_tries:
        try:
            async with AlertStreamer(session) as streamer:
                print("Yay! Connected!")
                ...
        except* HTTPXWSException:
            print("Oh no! Disconnected!")
            await sleep(tries ** 2)

Now we have persistence, exponential backoff, and disconnect/reconnect hooks--easy!
