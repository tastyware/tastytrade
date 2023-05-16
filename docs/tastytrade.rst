tastytrade
==========

Account
-------
.. module:: tastytrade.account

.. autoclass:: Account
   :members:

.. autotypeddict:: AccountBalance

.. autotypeddict:: AccountBalanceSnapshot

.. autotypeddict:: CurrentPosition

.. autotypeddict:: MarginRequirement

.. autotypeddict:: NetLiqOhlc

.. autotypeddict:: PositionLimit

.. autotypeddict:: Transaction

.. autotypeddict:: TradingStatus

Instruments
-----------
.. module:: tastytrade.instruments

.. autoclass:: Cryptocurrency
   :members:

.. autoclass:: Equity
   :members:

.. autoclass:: EquityOption
   :members:

.. autoclass:: Future
   :members:

.. autoclass:: FutureProduct
   :members:

.. autoclass:: FutureOption
   :members:

.. autoclass:: FutureOptionProduct
   :members:

.. autoclass:: Warrant
   :members:

Metrics
-------
.. module:: tastytrade.metrics

.. autofunction:: get_market_metrics

.. autofunction:: get_dividends

.. autofunction:: get_earnings

.. autotypeddict:: MarketMetricInfo

.. autotypeddict:: DividendInfo

.. autotypeddict:: EarningsInfo

Search
------
.. module:: tastytrade.search

.. autofunction:: symbol_search

.. autotypeddict:: SymbolData

Session
-------
.. module:: tastytrade.session

.. autoclass:: Session
   :members:

Streamer
--------
.. module:: tastytrade.streamer

.. autoclass:: SubscriptionType
   :members:

.. autoclass:: AlertStreamer
   :members:

.. autoclass:: DataStreamer
   :members:

.. autofunction:: _map_message

Utils
-----
.. module:: tastytrade.utils

.. autoclass:: TastytradeError
   :members:

.. autofunction:: validate_response

.. autofunction:: get_third_friday

.. autofunction:: snakeify

.. autofunction:: desnakeify

Watchlists
----------

.. module:: tastytrade.watchlists

.. autoclass:: PairsWatchlist
   :members:

.. autoclass:: Watchlist
   :members:
