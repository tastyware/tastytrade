Watchlists
==========

Watchlist actions
------------------------------
In order to perform watchlist actions you need to create a watchlist in the Tastytrade platform. 
In this example we will use 'MyWatchlist' for the purpose of removing and adding symbols to the already exising watchlist.

A session object is required to authenticate your requests to the Tastytrade API.

.. code-block:: python

   from tastytrade import ProductionSession
   session = ProductionSession(user, password)

A watchlist object is required to perform watchlist actions

.. code-block:: python

   from tastytrade.watchlists import Watchlist
   watchlist = 'MyWatchlist'
   current_watchlist = Watchlist.get_private_watchlist(session, watchlist).watchlist_entries

By default the Tastytrade API returns a list of dictionaries containing the symbol data. 

>>> name='MyWatchlist' watchlist_entries=[{'symbol': 'AAPL', 'instrument-type': 'Equity'}, {'symbol': 'MSFT', 'instrument-type': 'Equity'}] group_name='default' order_index=9999

Using the following code we extract only the ticker symbols

.. code-block:: python

   ticker_symbols = [ sub['symbol'] for sub in current_watchlist ]

>>> ticker_symbols = ['AAPL', 'MSFT']

Delete all symbols in 'MyWatchlist'

.. code-block:: python

   current_watchlist = Watchlist.get_private_watchlist(session, watchlist)
   
   for ticker in ticker_symbols:
      Watchlist.remove_symbol(current_watchlist, ticker, 'Equity')
   
   Watchlist.update_private_watchlist(current_watchlist, session)

>>> name='MyWatchlist' watchlist_entries=None group_name='default' order_index=9999

Add symbols to 'MyWatchlist'

.. code-block:: python

   instrument_type = 'Equity'
   
   current_watchlist = Watchlist.get_private_watchlist(session, watchlist)
   
   for ticker in ticker_symbols:
      Watchlist.add_symbol(current_watchlist, ticker, instrument_type)
   
   Watchlist.update_private_watchlist(current_watchlist, session)

>>> name='MyWatchlist' watchlist_entries=[{'symbol': 'AAPL', 'instrument-type': 'Equity'}, {'symbol': 'MSFT', 'instrument-type': 'Equity'}] group_name='default' order_index=9999
