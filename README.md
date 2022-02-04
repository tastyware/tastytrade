# Tastyworks API (Unofficial)

A simple, async-based, reverse-engineered API for tastyworks. This will allow you to create trading algorithms for whatever strategies you may have.

Please note that this is in the very early stages of development so any and all contributions are welcome. Please submit an issue and/or a pull request.

This is a fork with modified and added features. You can find the original GitHub repo at: https://github.com/boyan-soubachov/tastyworks_api

## Installation
```
$ pip install tastyworks-api
```

## Usage

Here's a simple example which showcases many different aspects of the API:

```python
import asyncio
from datetime import date
from decimal import Decimal as D

from tastyworks.models import option_chain, underlying
from tastyworks.models.greeks import Greeks
from tastyworks.models.option import Option, OptionType
from tastyworks.models.order import (Order, OrderDetails, OrderPriceEffect,
                                     OrderType)
from tastyworks.models.session import TastyAPISession
from tastyworks.models.trading_account import TradingAccount
from tastyworks.models.underlying import UnderlyingType
from tastyworks.streamer import DataStreamer
from tastyworks.tastyworks_api import tasty_session
from tastyworks.utils import get_third_friday


async def main_loop(session: TastyAPISession, streamer: DataStreamer):
    accounts = await TradingAccount.get_remote_accounts(session)
    acct = accounts[0]
    print(f'Accounts available: {accounts}')

    orders = await Order.get_remote_orders(session, acct)
    print(f'Number of active orders: {len(orders)}')

    # Execute an order
    details = OrderDetails(
        type=OrderType.LIMIT,
        price=D(400),
        price_effect=OrderPriceEffect.CREDIT)
    new_order = Order(details)

    opt = Option(
        ticker='AKS',
        quantity=1,
        expiry=get_third_friday(date.today()),
        strike=D(3),
        option_type=OptionType.CALL,
        underlying_type=UnderlyingType.EQUITY
    )
    new_order.add_leg(opt)

    res = await acct.execute_order(new_order, session, dry_run=True)
    print(f'Order executed successfully: {res}')

    # Get an options chain
    undl = underlying.Underlying('AKS')

    chain = await option_chain.get_option_chain(session, undl)
    print(f'Chain strikes: {chain.get_all_strikes()}')

    # Get all expirations for the options for the above equity symbol
    exp = chain.get_all_expirations()

    # Choose the next expiration as an example & fetch the entire options chain for that expiration (all strikes)
    next_exp = exp[0]
    chain_next_exp = await option_chain.get_option_chain(session, undl, next_exp)
    options = []
    for option in chain_next_exp.options:
        options.append(option)

    # Get the greeks data for all option symbols via the streamer by subscribing
    options_symbols = [options[x].symbol_dxf for x in range(len(options))]
    greeks_data = await streamer.stream('Greeks', options_symbols)

    for data in greeks_data:
        gd = Greeks().from_streamer_dict(data)
        # gd = Greeks(kwargs=data)
        idx_match = [options[x].symbol_dxf for x in range(len(options))].index(gd.symbol)
        options[idx_match].greeks = gd
        print('> Symbol: {}\tPrice: {}\tDelta {}'.format(gd.symbol, gd.price, gd.delta))


	quote = await streamer.stream('Quote', sub_values)
    print(f'Received item: {quote}')

	await streamer.close()


if __name__ == '__main__':
    tasty_client = tasty_session.create_new_session('foo', 'bar')
    streamer = DataStreamer(tasty_client)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main_loop(tasty_client, streamer))
    except Exception:
        print('Exception in main loop')
    finally:
        # find all futures/tasks still running and wait for them to finish
        pending_tasks = [
            task for task in asyncio.Task.all_tasks() if not task.done()
        ]
        loop.run_until_complete(asyncio.gather(*pending_tasks))
        loop.close()
```

## Guidelines and caveats

There are a few useful things to know which will help you get the most out of this API and use it in the way it was intended.

1. All objects are designed to be independent of each other in their _steady-state_. That is, unless executing an action, all objects are not bound to each other and have no knowledge of each other's awareness.
1. One can have multiple sessions and, due to the inter-object independence, can execute identical actions on identical objects in different sessions.
1. Given the above points, this API *does not* implement state management and synchronization (i.e. are my local object representations identical to the remote [Tastyworks] ones?). This is not an indefinitely closed matter and may be re-evaluated if the need arises.

## Disclaimer

This is an unofficial, reverse-engineered API for Tastyworks. There is no implied warranty for any actions and results which arise from using it.
The only guarantee I make is that you will lose all your money if you use this API.
