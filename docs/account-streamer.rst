Account Streamer
================

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
