Sync Contexts
=============

Since v12.0.0, the SDK is async-only. However, that doesn't mean there is no way make sync requests as before--you'll just have to jump through a few hoops to do so.

Blocking portals
----------------

``anyio`` provides a useful tool for stringing together async calls in a sync context called a blocking portal, which runs an event loop in a dedicated thread:

.. code-block:: python

   from functools import partial
   from anyio.from_thread import start_blocking_portal
   from tastytrade import Account, Session

   sesh = Session("secret", "refresh")
   with start_blocking_portal() as portal:
       acc = portal.call(Account.get, sesh, "5WX01234")
       print(
           portal.call(
               # we use partial since anyio functions don't support keyword arguments
               partial(acc.get_positions, sesh, underlying_symbols=["IBIT", "AVDV"])
           )
       )

This allows you to weave together sync and async calls seamlessly in a sync context. It even works with streamers, which wasn't possible before:

.. code-block:: python

    from tastytrade import DXLinkStreamer
    from tastytrade.dxfeed import Quote

    with start_blocking_portal() as portal:
        streamer = DXLinkStreamer(sesh)
        with portal.wrap_async_context_manager(streamer.__asynccontextmanager__()):
            portal.call(streamer.subscribe, Quote, ["SPY"])
            print(portal.call(streamer.get_event, Quote))

You can read more about this functionality in the `anyio docs <https://anyio.readthedocs.io/en/stable/threads.html#running-code-from-threads-using-blocking-portals>`_.
