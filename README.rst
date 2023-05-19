.. image:: https://readthedocs.org/projects/tastyworks-api/badge/?version=latest
   :target: https://tastyworks-api.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/tastytrade
   :target: https://pypi.org/project/tastytrade
   :alt: PyPI Package

.. image:: https://static.pepy.tech/badge/tastytrade
   :target: https://pepy.tech/project/tastytrade
   :alt: PyPI Downloads

Tastytrade Python SDK
=====================

.. inclusion-marker

A simple, reverse-engineered SDK for Tastytrade built on their (mostly) public API. This will allow you to create trading algorithms for whatever strategies you may have quickly and painlessly in Python.

Installation
------------

.. code-block:: bash

   $ pip install tastytrade

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
You can create a real session using your normal login, or a certification (test) session using your certification login.

.. code-block:: python

   from tastytrade.session import Session
   session = Session('username', 'password')

Using the streamer
------------------

The streamer is a websocket connection to the Tastytrade API that allows you to subscribe to real-time data for Quotes, Greeks, and more.

.. code-block:: python

   from tastytrade.streamer import DataStreamer, EventType

   streamer = await DataStreamer.create(session)
   subs_list = ['SPY', 'SPX']

   quotes = await streamer.oneshot(EventType.QUOTE, subs_list)
   print(quotes)

>>> [Quote(eventSymbol='SPY', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='Q', bidPrice=411.58, bidSize=400.0, askTime=0, askExchangeCode='Q', askPrice=411.6, askSize=1313.0), Quote(eventSymbol='SPX', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='\x00', bidPrice=4122.49, bidSize='NaN', askTime=0, askExchangeCode='\x00', askPrice=4123.65, askSize='NaN')]

Getting current positions
-------------------------

.. code-block:: python
   
   from tastytrade.account import Account

   account = Account.get_accounts(session)[0]
   positions = account.get_positions(session)
   print(positions[0])

>>> {'account-number': '########', 'symbol': 'INTC', 'instrument-type': 'Equity', 'underlying-symbol': 'INTC', 'quantity': 1, 'quantity-direction': 'Long', 'close-price': '29.8', 'average-open-price': '29.2997', 'average-yearly-market-close-price': '29.2997', 'average-daily-market-close-price': '29.8', 'multiplier': 1, 'cost-effect': 'Credit', 'is-suppressed': False, 'is-frozen': False, 'restricted-quantity': 0, 'realized-day-gain': '0.015', 'realized-day-gain-effect': 'Debit', 'realized-day-gain-date': '2023-05-15', 'realized-today': '0.015', 'realized-today-effect': 'Debit', 'realized-today-date': '2023-05-15', 'created-at': '2023-05-15T15:38:38.124+00:00', 'updated-at': '2023-05-15T15:42:08.991+00:00'}

Symbol search
-------------

.. code-block:: python

   from tastytrade.search import symbol_search

   results = symbol_search(session, 'AAP')
   print(results)

>>> [{'symbol': 'AAP', 'description': 'Advance Auto Parts Inc.'}, {'symbol': 'AAPL', 'description': 'Apple Inc. - Common Stock'}]

For more examples, check out the `documentation <https://tastyworks-api.readthedocs.io/en/latest/>`_.

Disclaimer
----------

This is an unofficial SDK for Tastytrade. There is no implied warranty for any actions and results which arise from using it.