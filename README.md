[![Docs](https://readthedocs.org/projects/tastyworks-api/badge/?version=latest)](https://tastyworks-api.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/tastytrade)](https://pypi.org/project/tastytrade)
[![Downloads](https://static.pepy.tech/badge/tastytrade)](https://pepy.tech/project/tastytrade)

# Tastytrade Python SDK

A simple, reverse-engineered SDK for Tastytrade built on their (now mostly public) API. This will allow you to create trading algorithms for whatever strategies you may have quickly and painlessly in Python.

> [!NOTE]
> Want to see the SDK in action? Check out [tastytrade-cli](https://github.com/tastyware/tastytrade-cli), a CLI for Tastytrade that showcases many of the SDK's features.

## Installation

```console
$ pip install tastytrade
```   

## Creating a session

A session object is required to authenticate your requests to the Tastytrade API.
You can create a real session using your normal login, or a certification (test) session using your certification login.

```python
from tastytrade import Session
session = Session('username', 'password')
```

## Using the streamer

The streamer is a websocket connection to dxfeed (the Tastytrade data provider) that allows you to subscribe to real-time data for quotes, greeks, and more.

```python
from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import EventType

async with DXLinkStreamer(session) as streamer:
    subs_list = ['SPY']  # list of symbols to subscribe to
    await streamer.subscribe(EventType.QUOTE, subs_list)
    # this example fetches quotes once, then exits
    quote = await streamer.get_event(EventType.QUOTE)
    print(quote)
```

```python
>>> [Quote(eventSymbol='SPY', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='Q', bidPrice=411.58, bidSize=400.0, askTime=0, askExchangeCode='Q', askPrice=411.6, askSize=1313.0), Quote(eventSymbol='SPX', eventTime=0, sequence=0, timeNanoPart=0, bidTime=0, bidExchangeCode='\x00', bidPrice=4122.49, bidSize='NaN', askTime=0, askExchangeCode='\x00', askPrice=4123.65, askSize='NaN')]
```

Note that this is asynchronous code, so you can't run it as is unless you're using a Jupyter notebook or something similar.

## Getting current positions

```python
from tastytrade import Account

account = Account.get_accounts(session)[0]
positions = account.get_positions(session)
print(positions[0])
```

```python
>>> CurrentPosition(account_number='5WX01234', symbol='IAU', instrument_type=<InstrumentType.EQUITY: 'Equity'>, underlying_symbol='IAU', quantity=Decimal('20'), quantity_direction='Long', close_price=Decimal('37.09'), average_open_price=Decimal('37.51'), average_yearly_market_close_price=Decimal('37.51'), average_daily_market_close_price=Decimal('37.51'), multiplier=1, cost_effect='Credit', is_suppressed=False, is_frozen=False, realized_day_gain=Decimal('7.888'), realized_day_gain_effect='Credit', realized_day_gain_date=datetime.date(2023, 5, 19), realized_today=Decimal('0.512'), realized_today_effect='Debit', realized_today_date=datetime.date(2023, 5, 19), created_at=datetime.datetime(2023, 3, 31, 14, 38, 32, 58000, tzinfo=datetime.timezone.utc), updated_at=datetime.datetime(2023, 5, 19, 16, 56, 51, 920000, tzinfo=datetime.timezone.utc), mark=None, mark_price=None, restricted_quantity=Decimal('0'), expires_at=None, fixing_price=None, deliverable_type=None)
```

## Placing an order

```python
from decimal import Decimal
from tastytrade import Account
from tastytrade.instruments import Equity
from tastytrade.order import NewOrder, OrderAction, OrderTimeInForce, OrderType, PriceEffect

account = Account.get_account(session, '5WX01234')
symbol = Equity.get_equity(session, 'USO')
leg = symbol.build_leg(Decimal('5'), OrderAction.BUY_TO_OPEN)  # buy to open 5 shares

order = NewOrder(
    time_in_force=OrderTimeInForce.DAY,
    order_type=OrderType.LIMIT,
    legs=[leg],  # you can have multiple legs in an order
    price=Decimal('10'),  # limit price, $10/share for a total value of $50
    price_effect=PriceEffect.DEBIT
)
response = account.place_order(session, order, dry_run=True)  # a test order
print(response)
```

```python
>>> PlacedOrderResponse(buying_power_effect=BuyingPowerEffect(change_in_margin_requirement=Decimal('125.0'), change_in_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, change_in_buying_power=Decimal('125.004'), change_in_buying_power_effect=<PriceEffect.DEBIT: 'Debit'>, current_buying_power=Decimal('1000.0'), current_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, new_buying_power=Decimal('874.996'), new_buying_power_effect=<PriceEffect.CREDIT: 'Credit'>, isolated_order_margin_requirement=Decimal('125.0'), isolated_order_margin_requirement_effect=<PriceEffect.DEBIT: 'Debit'>, is_spread=False, impact=Decimal('125.004'), effect=<PriceEffect.DEBIT: 'Debit'>), fee_calculation=FeeCalculation(regulatory_fees=Decimal('0.0'), regulatory_fees_effect=<PriceEffect.NONE: 'None'>, clearing_fees=Decimal('0.004'), clearing_fees_effect=<PriceEffect.DEBIT: 'Debit'>, commission=Decimal('0.0'), commission_effect=<PriceEffect.NONE: 'None'>, proprietary_index_option_fees=Decimal('0.0'), proprietary_index_option_fees_effect=<PriceEffect.NONE: 'None'>, total_fees=Decimal('0.004'), total_fees_effect=<PriceEffect.DEBIT: 'Debit'>), order=PlacedOrder(account_number='5WV69754', time_in_force=<OrderTimeInForce.DAY: 'Day'>, order_type=<OrderType.LIMIT: 'Limit'>, size='5', underlying_symbol='USO', underlying_instrument_type=<InstrumentType.EQUITY: 'Equity'>, status=<OrderStatus.RECEIVED: 'Received'>, cancellable=True, editable=True, edited=False, updated_at=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), legs=[Leg(instrument_type=<InstrumentType.EQUITY: 'Equity'>, symbol='USO', action=<OrderAction.BUY_TO_OPEN: 'Buy to Open'>, quantity=Decimal('5'), remaining_quantity=Decimal('5'), fills=[])], id=None, price=Decimal('50.0'), price_effect=<PriceEffect.DEBIT: 'Debit'>, gtc_date=None, value=None, value_effect=None, stop_trigger=None, contingent_status=None, confirmation_status=None, cancelled_at=None, cancel_user_id=None, cancel_username=None, replacing_order_id=None, replaces_order_id=None, in_flight_at=None, live_at=None, received_at=None, reject_reason=None, user_id=None, username=None, terminal_at=None, complex_order_id=None, complex_order_tag=None, preflight_id=None, order_rule=None), complex_order=None, warnings=[Message(code='tif_next_valid_sesssion', message='Your order will begin working during next valid session.', preflight_id=None)], errors=None)
```

## Options chain/streaming greeks

```python
from tastytrade import DXLinkStreamer
from tastytrade.instruments import get_option_chain
from tastytrade.utils import get_tasty_monthly

chain = get_option_chain(session, 'SPLG')
exp = get_tasty_monthly()  # 45 DTE expiration!
subs_list = [chain[exp][0].streamer_symbol]

async with DXLinkStreamer(session) as streamer:
    await streamer.subscribe(EventType.GREEKS, subs_list)
    greeks = await streamer.get_event(EventType.GREEKS)
    print(greeks)
```

```python
>>> [Greeks(eventSymbol='.SPLG230616C23', eventTime=0, eventFlags=0, index=7235129486797176832, time=1684559855338, sequence=0, price=26.3380972233688, volatility=0.396983376650804, delta=0.999999999996191, gamma=4.81989763184255e-12, theta=-2.5212017514875e-12, rho=0.01834504287973133, vega=3.7003015672215e-12)]
```

For more examples, check out the [documentation](https://tastyworks-api.readthedocs.io/en/latest/).
        
## Disclaimer

This is an unofficial SDK for Tastytrade. There is no implied warranty for any actions and results which arise from using it.
