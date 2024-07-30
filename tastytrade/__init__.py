import logging

API_URL = 'https://api.tastyworks.com'
CERT_URL = 'https://api.cert.tastyworks.com'
VERSION = '8.2'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# flake8: noqa

from .account import Account
from .instruments import (Cryptocurrency, Equity, Future, FutureOption,
                          FutureOptionProduct, FutureProduct,
                          NestedFutureOptionChain, NestedOptionChain, Option,
                          OptionType, Warrant, get_future_option_chain,
                          get_option_chain, get_quantity_decimal_precisions)
from .metrics import (get_dividends, get_earnings, get_market_metrics,
                      get_risk_free_rate)
from .order import (ComplexOrderType, InstrumentType, NewComplexOrder,
                    NewOrder, OrderAction, OrderStatus, OrderTimeInForce,
                    OrderType, PriceEffect)
from .search import symbol_search
from .session import Session
from .streamer import AlertStreamer, AlertType, DXLinkStreamer
from .utils import (get_future_fx_monthly, get_future_grain_monthly,
                    get_future_index_monthly, get_future_metal_monthly,
                    get_future_oil_monthly, get_future_treasury_monthly,
                    get_tasty_monthly, get_third_friday, now_in_new_york,
                    today_in_new_york)
from .watchlists import PairsWatchlist, Watchlist

__all__ = [
    'Account',
    'AlertStreamer',
    'AlertType',
    'ComplexOrderType',
    'Cryptocurrency',
    'DXLinkStreamer',
    'Equity',
    'Future',
    'FutureOption',
    'FutureOptionProduct',
    'FutureProduct',
    'InstrumentType',
    'NestedFutureOptionChain',
    'NestedOptionChain',
    'NewComplexOrder',
    'NewOrder',
    'Option',
    'OptionType',
    'OrderAction',
    'OrderStatus',
    'OrderTimeInForce',
    'OrderType',
    'PairsWatchlist',
    'PriceEffect',
    'Session',
    'Warrant',
    'Watchlist',
    'get_dividends',
    'get_earnings',
    'get_future_fx_monthly',
    'get_future_grain_monthly',
    'get_future_index_monthly',
    'get_future_metal_monthly',
    'get_future_oil_monthly',
    'get_future_option_chain',
    'get_future_treasury_monthly',
    'get_market_metrics',
    'get_option_chain',
    'get_quantity_decimal_precisions',
    'get_risk_free_rate',
    'get_tasty_monthly',
    'get_third_friday',
    'now_in_new_york',
    'symbol_search',
    'today_in_new_york'
]
