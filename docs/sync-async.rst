sync/async
==========

After creating a session (which is always initialized synchronously), the rest of the API endpoints implemented in the SDK have both sync and async implementations as of version 9.0.

Let's see how this looks:

.. code-block:: python

    from tastytrade Account, Session
    session = Session(username, password)
    # using sync implementation
    accounts = Account.get_accounts(session)

The async implementation is similar:

.. code-block:: python

    from tastytrade Account, Session
    session = Session(username, password)
    # using async implementation
    accounts = await Account.a_get_accounts(session)

That's it! All sync methods have a parallel async method that starts with `a_`.

.. note::
   Please note that two modules, `tastytrade.backtest` and `tastytrade.streamer`, only have async implementations. But for everything else, you can use what you'd like!
