# TastyTrade API: Market Data

## About
The 'market-data' end point returns Quote and Trading information for many symbols, up to 100 accross all symbol types. The information changes throughout the trading day. Fields include bid, ask, volume, and open interest (options only).

## Method
GET

## URL Path
/market-data/by-type

## Query Parameters
cryptocurrency: Comma-separated list of cryptocurrency symbols. example: BTC/USD
equity:         Comma-separated list of equity symbols. example: AAPL
equity-option:  Comma-separated list of equity option symbols. example: SPY 250428P00355000,SPY 250428C00355000
index:          Comma-separated list of index symbols. example: SPX,VIX
future:         Comma-separated list of future symbols. example:  /CLM5
future-option:  Comma-separated list of future option symbols. example:  /MESU5EX3M5 250620C6450

## Headers
Authorization: TT_AUTH_TOKEN
Content-Type: application/json
