Sessions
========

Creating an OAuth application
-----------------------------

A session object is required to authenticate your requests to the Tastytrade API. Tastytrade uses OAuth logins, which allow you to connect applications (third-party or private) to your trading account to use the API.

To get started, create a new OAuth application `here <https://my.tastytrade.com/app.html#/manage/api-access/oauth-applications>`_. Check all the scopes you plan to use, add `http://localhost:8000` as a valid callback, and create the application. **Save the client secret**, you'll need it later!

Generating an initial refresh token
-----------------------------------

In order to generate an initial refresh token, you have two options. The easiest way is to simply generate one from Tastytrade's website: go to OAuth Applications > Manage > Create Grant to get a new refresh token, **which you should also save**.

At this point, OAuth is now setup correctly! Doing these steps once is sufficient for **indefinite usage** of ``Session`` for authentication to the API, since refresh tokens never expire. From now on you can simply authenticate with your client secret and refresh token.

Creating a session
------------------

.. code-block:: python

   from tastytrade import Session

   session = Session('client_secret', 'refresh_token')

These session objects can be used to make API requests:

.. code-block:: python

   from tastytrade import Account

   accounts = Account.get(session)

Note that OAuth sessions make API requests using a special session token, which has a duration of only 15 minutes. However, since the refresh tokens last forever, you can call ``Session.refresh()`` to refresh the session token whenever needed. The session object will keep track of session expiration time for you to make it easier to know when to refresh:

.. code-block:: python

   from tastytrade.utils import now_in_new_york

   if now_in_new_york() > session.session_expiration:
       session.refresh()
       print(Account.get(session))

A sandbox account for testing can be created `here <https://developer.tastytrade.com/sandbox/>`_, then used to create a session in the same way:

.. code-block:: python

   from tastytrade import Session
   session = Session('client_secret', 'refresh_token', is_test=True)
