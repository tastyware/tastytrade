Paper API
=========

Although Tastytrade offers a sandbox environment, it is unfortunately not very useful for testing for a few reasons:

* limited symbol support (only supports a few underlyings)

* no ability to control order fills

* environment gets reset every 24 hours

In order to get around these limitations, tastyware provides access to a proprietary paper trading API for paid subscribers. The paper trading endpoints are designed to emulate the actual API as closely as possible to allow you to test your code in the same way you'd write production code.

If you've made significant contributions to the SDK, please reach out to `support@tastyware.dev <mailto:support@tastyware.dev>`_ and ask for a free API key. If you sponsor tastyware at a level of $30/month or above, you should be able to log in and create an API key already! Otherwise, if you've benefitted from this project and would make good use of the paper API, please consider subscribing--it's a great way to support the project!

.. warning::

   At this time, the paper API only supports equities/index options trades. I hope to add futures options and other instrument types soon.

.. note::

   The paper API is still in beta. If you run into any issues or questions, reach out via `Matrix <https://matrix.to/#/!PxsVtmffaZAheSDHyX:gitter.im?via=gitter.im>`_!

Creating a tastyware API key
----------------------------

To get started, log in with GitHub and subscribe to tastyware `here <https://tastyware.dev/login>`_. Once you've subscribed you'll be able to generate a new API key. **Save the API key**, you'll only be able to see it once!

.. tip::

   You can manage your subscription, regenerate your API key, or view API docs at any time `here <https://tastyware.dev/login>`_!

Creating a session
------------------

Now that you have your API key, you can use it to create a :class:`~tastytrade.paper.PaperSession`:

.. code-block:: python

   from tastytrade.paper import PaperSession

   paper = PaperSession("MY-API-KEY")

These session objects can be used to make API requests to most **account-related endpoints** in the same way you'd use a normal session:

.. code-block:: python

   from tastytrade import Account

   accounts = await Account.get(paper)

.. info::

   Paper API endpoints have a default rate limit of 5 requests/second. If you need a higher limit or have a unique use case, please reach out to `support <mailto:support@tastyware.dev>`_.

:class:`~tastytrade.paper.PaperSession` contains a few helper functions for managing paper accounts:

.. code-block:: python

   # create a new paper account
   paper_account = await paper.create_account("Paper", margin_or_cash="Cash", initial_deposit=100_000)
   # deposit some cash into the account (negative numbers are withdrawals)
   await paper.deposit(paper_account, Decimal(40))
   # delete the account and its transactions
   await paper.delete_account(paper_account)

Writing paper trading applications
----------------------------------

The paper session can only be used with account-related endpoints. For non-account endpoints, just use a normal Tastytrade session:

.. code-block:: python

   from tastytrade import Session
   from tastytrade.paper import PaperSession

   session = Session("MY-SECRET", "MY-REFRESH")
   paper = PaperSession("MY-API-KEY")

Here's an example of how one might combine a normal and a paper session to simulate production code:

.. code-block:: python

   # here, we use a normal session for the generic option chain endpoint
   chain = (await get_option_chain(session, "SPX"))[date(2026, 4, 17)]
   option = next(
       c
       for c in chain
       if c.option_type == OptionType.CALL and round(c.strike_price) == 7000
   )
   # here, we use a paper session to simulate placing orders with the chosen option
   acc = await Account.get(paper, "TW000014")
   order = NewOrder(
       time_in_force=OrderTimeInForce.DAY,
       order_type=OrderType.LIMIT,
       legs=[option.build_leg(1, OrderAction.BUY_TO_OPEN)],
       price=-Decimal("3"),
   )
   print(await acc.place_order(paper, order, dry_run=True))

Using the paper account streamer
--------------------------------

The :class:`~tastytrade.streamer.AlertStreamer` class is very important in most production apps for tracking whether orders have been filled or not. Fortunately the paper API provides a similar streamer that can be used with minimal code changes:

.. code-block:: python

   from tastytrade.paper import PaperAlertStreamer

   async with PaperAlertStreamer(paper) as streamer:
       await streamer.subscribe_accounts([acc])
       async for msg in streamer.listen(PlacedOrder):
           print(msg)

.. note::

   :class:`~tastytrade.paper.PaperAlertStreamer` only supports listening to order notifications at this time.

Controlling order fills
-----------------------

One of the most important features that distinguishes the paper API from the official Tastytrade sandbox is the ability to control order fill behavior. This is done through :class:`~tastytrade.order.FillBehavior`:

.. code-block:: python

   from tastytrade.order import (
       FillBehavior,
       NewOrder,
       OrderAction,
       OrderTimeInForce,
       OrderType,
   )

   order = NewOrder(
       time_in_force=OrderTimeInForce.DAY,
       order_type=OrderType.LIMIT,
       legs=[option.build_leg(1, OrderAction.BUY_TO_OPEN)],
       price=-Decimal("3"),
       behavior=FillBehavior.SCHEDULED,
       schedule=datetime(...),
   )

Via :class:`~tastytrade.order.FillBehavior` you can configure a custom delay, a specific fill time, immediate fill/rejection of an order, or even partial fills!

The paper API works just as well outside of normal market hours, so :class:`~tastytrade.order.OrderTimeInForce` is just a formality.

Writing unit tests
------------------

The paper API makes writing unit tests for your code straightforward:

.. code-block:: python

   pytestmark = pytest.mark.anyio

   @pytest.fixture(scope="module")
   async def paper():
       yield PaperSession(...)

   @pytest.fixture(scope="module")
   async def account(paper: PaperSession):
       async with paper.temporary_account() as acc:
           yield acc

   async def test_place_and_cancel_order(
       account: Account, paper: PaperSession, session: Session
   ):
       chain = (await get_option_chain(session, "SPX"))[date(...)]
       option = next(
           c
           for c in chain
           if c.option_type == OptionType.CALL and round(c.strike_price) == 7000
       )
       order = NewOrder(
           time_in_force=OrderTimeInForce.DAY,
           order_type=OrderType.LIMIT,
           legs=[option.build_leg(1, OrderAction.BUY_TO_OPEN)],
           price=-Decimal("3"),
           behavior=FillBehavior.DELAYED,
           delay=5,
       )
       res = await account.place_order(paper, order, dry_run=False)
       await account.delete_order(paper, res.order.id)

Here, we use the :attr:`~tastytrade.paper.PaperSession.temporary_account` context manager to create an account, which can then be used to run tests and finally gets cleaned up--nifty!
