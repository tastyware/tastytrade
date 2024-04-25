Watchlists
==========

In this example assume ``MyWatchlist`` is an exising watchlist we want to modify.

To use watchlists you'll need a production session:

.. code-block:: python

   from tastytrade import Session
   session = Session(user, password)

Now we can fetch the watchlist:

.. code-block:: python

   from tastytrade import Watchlist
   watchlist = Watchlist.get_private_watchlist(session, 'MyWatchlist')
   print(watchlist.watchlist_entries)

>>> [{'symbol': 'AAPL', 'instrument-type': 'Equity'}, {'symbol': 'MSFT', 'instrument-type': 'Equity'}]

To add a symbol to the watchlist:

.. code-block:: python

   from tastytrade.instruments import InstrumentType
   Watchlist.add_symbol('SPY', InstrumentType.EQUITY)
   
In this case, the symbol is present locally, but not remotely, so we need to update the remote list:

.. code-block:: python

   watchlist.update_private_watchlist(session)

We can also create a new watchlist from scratch, then publish it to the Tastytrade server:

.. code-block:: python

   new_watchlist = Watchlist(name='NewWatchlist')
   new_watchlist.add_symbol('USO', InstrumentType.EQUITY)
   new_watchlist.upload_private_watchlist(session)
