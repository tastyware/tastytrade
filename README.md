[![PyPI version](https://badge.fury.io/py/tastytrade.svg)](https://badge.fury.io/py/tastytrade)
[![Downloads](https://pepy.tech/badge/tastytrade)](https://pepy.tech/project/tastytrade)
[![Docs](https://readthedocs.org/projects/tastytrade/badge/?version=latest)](https://tastytrade.readthedocs.io/en/latest/?badge=latest)

# Tastytrade API (unofficial)

A simple, async-based, reverse-engineered API for tastytrade. This will allow you to create trading algorithms for whatever strategies you may have.

Please note that this is in the very early stages of development so any and all contributions are welcome. Please submit an issue and/or a pull request.

This is a fork with modified and added features. You can find the original (unmaintained) GitHub repo at: https://github.com/boyan-soubachov/tastyworks_api

## Installation
```
$ pip install tastytrade
```

## Guidelines and caveats

There are a few useful things to know which will help you get the most out of this API and use it in the way it was intended.

1. All objects are designed to be independent of each other in their _steady-state_. That is, unless executing an action, all objects are not bound to each other and have no knowledge of each other's awareness.
1. One can have multiple sessions and, due to the inter-object independence, can execute identical actions on identical objects in different sessions.
1. Given the above points, this API *does not* implement state management and synchronization (i.e. are my local object representations identical to the remote [Tastytrade] ones?). This is not an indefinitely closed matter and may be re-evaluated if the need arises.

## Disclaimer

This is an unofficial, reverse-engineered API for Tastytrade. There is no implied warranty for any actions and results which arise from using it.
The only guarantee I make is that you will lose all your money if you use this API.
