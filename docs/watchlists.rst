Watchlists
==========
Watchlist actions
------------------------------

.. code-block:: python

   from tastytrade.watchlists import Watchlist
   from tastytrade import ProductionSession
   
   session = ProductionSession(user, password)
   watchlist = 'MyWatchlist'
   
   #Get symbols as a list
   temp_watchlist = Watchlist.get_private_watchlist(session, watchlist).watchlist_entries
   watchlist_entries = [ sub['symbol'] for sub in temp_watchlist ]
   
   #Delete all symbols in 'MyWatchlist'
   current_watchlist = Watchlist.get_private_watchlist(session, watchlist)
   
   for ticker in watchlist_entries:
      Watchlist.remove_symbol(current_watchlist, ticker, 'Equity')
   
   Watchlist.update_private_watchlist(current_watchlist, session)
   
   #Add symbol to 'MyWatchlist'
   ticker_list = ['AAPL', 'MSFT']
   instrument_type= 'Equity'
   
   current_watchlist = Watchlist.get_private_watchlist(session, watchlist)
   
   for ticker in ticker_list:
      Watchlist.add_symbol(current_watchlist, ticker, instrument_type)
   
   Watchlist.update_private_watchlist(current_watchlist, session)

>>> Watchlist actions completed
