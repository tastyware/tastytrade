Getting Started
===============

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
You can create a real session using your normal login, or a certification (test) session using your certification login.

.. code-block:: python

   from tastyworks.session import Session
   session = Session('username', 'password')

Using the streamer
-------------------

The streamer is a websocket connection to the Tastytrade API that allows you to subscribe to real-time data for Quotes, Greeks, and more.

.. code-block:: python

   from tastyworks.session import Session
   from tastyworks.streamer import DataStreamer, EventType

   session = Session('username', 'password')
   streamer = await DataStreamer.create(session)
   subs_list = ['SPY', 'SPX']

   quotes = await streamer.stream(EventType.QUOTE, subs_list)
   print(quotes)