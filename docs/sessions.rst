Sessions
========

Creating a session
------------------

A session object is required to authenticate your requests to the Tastytrade API.
To create a production (real) session using your normal login:

.. code-block:: python

   from tastytrade import Session
   session = Session('username', 'password')

A certification (test) account can be created `here <https://developer.tastytrade.com/sandbox/>`_, then used to create a session.

.. code-block:: python

   from tastytrade import Session
   session = Session('username', 'password', is_test=True)

You can make a session persistent by generating a remember token, which is valid for 24 hours:

.. code-block:: python

   session = Session('username', 'password', remember_me=True)
   remember_token = session.remember_token
   # remember token replaces the password for the next login
   new_session = Session('username', remember_token=remember_token)

.. note::
   If you used a certification (test) account to create the session associated with the `remember_token`, you must set `is_test=True` when creating subsequent sessions.

OAuth sessions
--------------

Tastytrade has recently added support for OAuth logins, which allow you to connect an application for the purposes of managing trades on your behalf. Apart from allowing you to connect to 3rd-party apps (or build your own), you can also build a private OAuth application, which provides better security compared to username/password authentication since you don't have to expose your login information.

To get started, create a new OAuth application `here <https://my.tastytrade.com/app.html#/manage/api-access/oauth-applications>`_. You'll need to check all the scopes and save the client ID and client secret. Then, run this code:

.. code-block:: python

   from tastytrade.oauth import login

   login()

This will open up a web interface in your browser where you'll be prompted to paste your client ID and client secret. These credentials will then be used to connect your application to Tastytrade. After following the steps in your browser, you should see your refresh token in the browser and in the console, which you should save.

At this point, OAuth is now setup correctly! Doing the above once is sufficient for **indefinite usage** of ``OAuthSession`` for authentication to the API, since refresh tokens never expire. From now on you can simply authenticate like so:

.. code-block:: python

   from tastytrade import OAuthSession

   session = OAuthSession('my-client-secret', 'my-refresh-token')

These session objects can be used almost anywhere you can use a normal session:

.. code-block:: python

   from tastytrade import Account

   accounts = Account.get(session)

Note that OAuth sessions make API requests using a special session token, which has a duration of only 15 minutes. However, since the refresh tokens last forever, you can call ``OAuthSession.refresh()`` to refresh the session token whenever needed. The session object will keep track of session expiration time for you to make it easier to know when to refresh:

.. code-block:: python

   from tastytrade.utils import now_in_new_york

   if now_in_new_york() > session.session_expiration:
       session.refresh()
       print(Account.get(session))
