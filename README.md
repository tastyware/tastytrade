[![Docs](https://readthedocs.org/projects/tastyworks-api/badge/?version=latest)](https://tastyworks-api.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/tastytrade)](https://pypi.org/project/tastytrade)
[![Downloads](https://static.pepy.tech/badge/tastytrade)](https://pepy.tech/project/tastytrade)
[![Release)](https://img.shields.io/github/v/release/tastyware/tastytrade?label=release%20notes)](https://github.com/tastyware/tastytrade/releases)

# Tastytrade Python SDK

A simple, asynchronous SDK for Tastytrade's public API. This will allow you to create trading algorithms for whatever strategies you may have quickly and painlessly in Python.

## Features

- Up to 10x less code than using the API directly
- Powerful websocket implementation for account alerts and data streaming
- 100% typed, with Pydantic models for all JSON responses from the API
- 95%+ unit test coverage
- Comprehensive documentation
- Utility functions for timezone calculations, futures monthly expiration dates, and more
- Proprietary paper API for reliable testing

> [!TIP]
> Want to see the SDK in action? Check out [tastytrade-cli](https://github.com/tastyware/tastytrade-cli), a CLI for Tastytrade that showcases many of the SDK's features.

## Installation

```console
$ pip install tastytrade
```

## Creating a session

A session object is required to authenticate your requests to the Tastytrade API. See [here](https://tastyworks-api.readthedocs.io/en/latest/sessions.html) for information on how to set up an OAuth application.

```python
from tastytrade import Session
session = Session('client_secret', 'refresh_token')
```

## Using the streamer

The streamer is a websocket connection to dxfeed (the Tastytrade data provider) that allows you to subscribe to real-time data for quotes, greeks, and more.

```python
from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Quote

async with DXLinkStreamer(session) as streamer:
    subs_list = ['SPY']  # list of symbols to subscribe to
    await streamer.subscribe(Quote, subs_list)
    # fetch a single quote
    quote = await streamer.get_event(Quote)
    print(quote)
    # or multiple quotes...
    async for quote in streamer.listen(Quote):
        print(quote)
```

```python
>>> event_symbol='SPY' event_time=0 sequence=0 time_nano_part=0 bid_time=0 bid_exchange_code='Q' ask_time=0 ask_exchange_code='Q' bid_price=Decimal('742.59') ask_price=Decimal('742.62') bid_size=Decimal('170.0') ask_size=Decimal('240.0')
```

## Getting current positions

```python
from tastytrade import Account

account = (await Account.get(session))[0]
positions = await account.get_positions(session)
print(positions[0])
```

```python
>>> account_number='5WX01234' symbol='BRK/B' instrument_type=<InstrumentType.EQUITY: 'Equity'> underlying_symbol='BRK/B' quantity=Decimal('1') quantity_direction='Long' close_price=Decimal('499.74') average_open_price=Decimal('477.34') multiplier=Decimal('1.0') cost_effect='Credit' created_at=datetime.datetime(2026, 4, 17, 14, 23, 1, 210000, tzinfo=TzInfo(0)) updated_at=datetime.datetime(2026, 6, 9, 20, 2, 32, 427000, tzinfo=TzInfo(0)) average_yearly_market_close_price=Decimal('477.34') average_daily_market_close_price=Decimal('499.74') realized_day_gain_date=datetime.date(2026, 6, 9) realized_today_date=datetime.date(2026, 6, 9)
```

## Placing an order

```python
from decimal import Decimal
from tastytrade import Account
from tastytrade.instruments import Equity
from tastytrade.order import LimitOrder, OrderAction

account = await Account.get(session, '5WX01234')
symbol = await Equity.get(session, 'USO')
leg = symbol.build_leg(5, OrderAction.BUY_TO_OPEN)  # buy to open 5 shares

order = LimitOrder(
    legs=[leg],  # you can have multiple legs in an order
    price=Decimal('-10')  # limit price, $10/share debit for a total value of $50
)
response = await account.place_order(session, order, dry_run=True)  # a test order
print(response)
```

```python
>>> buying_power_effect=BuyingPowerEffect(change_in_margin_requirement=Decimal('-50.0') change_in_buying_power=Decimal('-50.004') current_buying_power=Decimal('190.95') new_buying_power=Decimal('140.946') isolated_order_margin_requirement=Decimal('-50.0') impact=Decimal('50.004') effect=<PriceEffect.DEBIT: 'Debit'>) order=UnplacedOrder(account_number='5WX01234' time_in_force=<OrderTimeInForce.DAY: 'Day'> order_type=<OrderType.LIMIT: 'Limit'> underlying_symbol='USO' underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'> status=<OrderStatus.RECEIVED: 'Received'> cancellable=True editable=True updated_at=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=TzInfo(0)) legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'> symbol='USO' action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'> quantity=5 remaining_quantity=Decimal('5'))] size=Decimal('5') price=Decimal('-10.0') source='tastyware/tastytrade:v13.0.0') fee_calculation=FeeCalculation(clearing_fees=Decimal('-0.004') total_fees=Decimal('-0.004'))
```

## Options chain/streaming greeks

```python
from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Greeks
from tastytrade.instruments import get_option_chain
from tastytrade.utils import get_tasty_monthly

chain = await get_option_chain(session, 'SPY')
exp = get_tasty_monthly()  # 45 DTE expiration!
subs_list = [chain[exp][0].streamer_symbol]

async with DXLinkStreamer(session) as streamer:
    await streamer.subscribe(Greeks, subs_list)
    greeks = await streamer.get_event(Greeks)
    print(greeks)
```

```python
>>> event_symbol='.SPY260821C360' event_time=0 event_flags=0 index=7657999377268473856 time=1783016924113 sequence=0 price=Decimal('383.872914648466') volatility=Decimal('0.945267732851094') delta=Decimal('0.987555718428321') gamma=Decimal('0.0001239745502605713') theta=Decimal('-0.0836282191559167') rho=Decimal('0.479468024985951') vega=Decimal('0.0886597706581432')
```

For more examples, check out the [documentation](https://tastyworks-api.readthedocs.io/en/latest/).

## Disclaimer

This is an unofficial SDK for Tastytrade. There is no implied warranty for any actions and results which arise from using it.
