tastytrade
==========

Account
-------
.. module:: tastytrade.account

.. autoclass:: Account
   :members:

.. autoclass:: AccountBalance
   :members:

.. autoclass:: AccountBalanceSnapshot
   :members:

.. autoclass:: CurrentPosition
   :members:

.. autoclass:: Lot
   :members:

.. autoclass:: MarginReport
   :members:

.. autoclass:: MarginReportEntry
   :members:

.. autoclass:: MarginRequirement
   :members:

.. autoclass:: NetLiqOhlc
   :members:

.. autoclass:: PositionLimit
   :members:

.. autoclass:: TradingStatus
   :members:

.. autoclass:: Transaction
   :members:

Instruments
-----------
.. module:: tastytrade.instruments

.. autoclass:: Cryptocurrency
   :members:

.. autoclass:: DestinationVenueSymbol
   :members:

.. autoclass:: TickSize
   :members:

.. autoclass:: Equity
   :members:

.. autoclass:: Option
   :members:

.. autoenum:: OptionType

.. autoclass:: Deliverable
   :members:

.. autoclass:: Strike
   :members:

.. autoclass:: NestedOptionChain
   :members:

.. autoclass:: NestedOptionChainExpiration
   :members:

.. autoclass:: Future
   :members:

.. autoenum:: FutureMonthCode

.. autoclass:: FutureProduct
   :members:

.. autoclass:: FutureOption
   :members:

.. autoclass:: FutureOptionProduct
   :members:

.. autoclass:: FutureEtfEquivalent
   :members:

.. autoclass:: Roll
   :members:

.. autoclass:: Warrant
   :members:

.. autofunction:: get_quantity_decimal_precisions

.. autoclass:: QuantityDecimalPrecision
   :members:

.. autofunction:: get_option_chain

.. autofunction:: get_future_option_chain

Metrics
-------
.. module:: tastytrade.metrics

.. autofunction:: get_market_metrics

.. autofunction:: get_dividends

.. autofunction:: get_earnings

.. autoclass:: MarketMetricInfo
   :members:

.. autoclass:: Liquidity
   :members:

.. autoclass:: OptionExpirationImpliedVolatility
   :members:

.. autoclass:: DividendInfo
   :members:

.. autoclass:: EarningsInfo
   :members:

Order
-----

.. autoenum:: PriceEffect

.. autoenum:: OrderType

.. autoenum:: OrderStatus

.. autoenum:: TimeInForce

Search
------
.. module:: tastytrade.search

.. autofunction:: symbol_search

.. autoclass:: SymbolData
   :members:

Session
-------
.. module:: tastytrade.session

.. autoclass:: Session
   :members:

Streamer
--------
.. module:: tastytrade.streamer

.. autoenum:: SubscriptionType

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

.. autoclass:: TastytradeJsonDataclass
   :members:

.. autofunction:: validate_response

Watchlists
----------

.. module:: tastytrade.watchlists

.. autoclass:: PairsWatchlist
   :members:

.. autoclass:: Pair
   :members:

.. autoclass:: Watchlist
   :members:
