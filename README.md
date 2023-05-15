[![Docs](https://readthedocs.org/projects/tastyworks-api/badge/?version=latest)](https://tastyworks-api.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/tastytrade)](https://pypi.org/project/tastytrade)
[![Downloads](https://static.pepy.tech/badge/tastytrade)](https://pepy.tech/project/tastytrade)

# Tastytrade Python SDK

A simple, async-based, reverse-engineered SDK for Tastytrade built on their (mostly) public API. This will allow you to create trading algorithms for whatever strategies you may have quickly and painlessly in Python.

## Installation

```
$ pip install tastytrade
```

## Getting Started

Here's a simple example to get you started. For more information, check out the [documentation](https://tastyworks-api.readthedocs.io/en/latest/).

```python
from tastytrade.dxfeed.event import EventType
from tastytrade.session import Session
from tastytrade.streamer import Streamer

session = Session('username', 'password')
streamer = await Streamer.create(session)

tickers = ['SPX', 'GLD']
quotes = await streamer.oneshot(EventType.QUOTE, tickers)
print(quotes)
```

## Disclaimer

This is an unofficial SDK for Tastytrade. There is no implied warranty for any actions and results which arise from using it.
