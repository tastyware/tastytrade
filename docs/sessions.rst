Sessions
========

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
To create a production (real) session using your normal login:

.. code-block:: python

   from tastytrade import Session
   session = Session('username', 'password')

A certification (test) account can be created `here <https://developer.tastytrade.com/sandbox/>`_, then used to create a session:

.. code-block:: python

   from tastytrade import Session
   session = Session('username', 'password', is_test=True)

You can make a session persistent by generating a remember token, which is valid for 24 hours:

.. code-block:: python

   session = Session('username', 'password', remember_me=True)
   remember_token = session.remember_token
   # remember token replaces the password for the next login
   new_session = Session('username', remember_token=remember_token)
