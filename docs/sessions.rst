Sessions and Events
===================

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
To create a real session (using your normal login):

.. code-block:: python

   from tastytrade.session import Session
   session = Session('username', 'password')

A certification (test) account can be created `here <https://developer.tastytrade.com/sandbox/>`_, then used to create a session:

.. code-block:: python

   from tastytrade.session import Session
   session = Session('username', 'password', is_certification=True)
