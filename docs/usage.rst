Usage
=====

.. code-block:: python

   from tastyworks.session import Session
   from tastyworks.streamer import DataStreamer, EventType

   session = Session('username', 'password')
   streamer = await DataStreamer.create(session)
   subs_list = ['SPY', 'GLD']
   quotes = await streamer.stream(EventType.QUOTE, subs_list)
   print(quotes)
