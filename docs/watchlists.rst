Watchlists
==========

To use watchlists you'll need a production session:

.. code-block:: python

   from tastytrade import Session
   session = Session(user, password)

Let's fetch an existing watchlist:

.. code-block:: python

   from tastytrade import PrivateWatchlist
   watchlist = PrivateWatchlist.get(session, 'MyWatchlist')
   print(watchlist.watchlist_entries)

>>> [{'symbol': 'AAPL', 'instrument-type': 'Equity'}, {'symbol': 'MSFT', 'instrument-type': 'Equity'}]

To add a symbol to the watchlist:

.. code-block:: python

   from tastytrade.instruments import InstrumentType
   watchlist.add_symbol('SPY', InstrumentType.EQUITY)

In this case, the symbol is present locally, but not remotely, so we need to update the remote list:

.. code-block:: python

   watchlist.update(session)

We can also create a new watchlist from scratch, then publish it to the Tastytrade server:

.. code-block:: python

   new_watchlist = PrivateWatchlist(name='NewWatchlist')
   new_watchlist.add_symbol('USO', InstrumentType.EQUITY)
   new_watchlist.upload(session)

You can also fetch public watchlists:

.. code-block:: python

   from tastytrade import PublicWatchlist
   public_watchlist = PublicWatchlist.get(session, "Tom's Watchlist")
   print(public_watchlist.watchlist_entries)
