from datetime import date, datetime
from decimal import Decimal

from tastytrade.session import Session
from tastytrade.utils import TastytradeData, validate_and_parse


class DividendInfo(TastytradeData):
    """
    Dataclass representing dividend information for a given symbol.
    """

    occurred_date: date
    amount: Decimal


class EarningsInfo(TastytradeData):
    """
    Dataclass representing earnings information for a given symbol.
    """

    occurred_date: date
    eps: Decimal


class EarningsReport(TastytradeData):
    """
    Dataclass containing information about a recent earnings report, or the
    expected date of the next one.
    """

    estimated: bool
    late_flag: int
    visible: bool
    actual_eps: Decimal | None = None
    consensus_estimate: Decimal | None = None
    expected_report_date: date | None = None
    quarter_end_date: date | None = None
    time_of_day: str | None = None
    updated_at: datetime | None = None


class Liquidity(TastytradeData):
    """
    Dataclass representing liquidity information for a given symbol.
    """

    sum: Decimal
    count: int
    started_at: datetime
    updated_at: datetime | None = None


class OptionExpirationImpliedVolatility(TastytradeData):
    """
    Dataclass containing implied volatility information for a given symbol
    and expiration date.
    """

    expiration_date: date
    settlement_type: str
    option_chain_type: str
    implied_volatility: Decimal | None = None


class MarketMetricInfo(TastytradeData):
    """
    Dataclass representing market metrics for a given symbol.

    Contains lots of useful information, like IV rank, IV percentile and beta.
    """

    symbol: str
    implied_volatility_index: Decimal | None = None
    implied_volatility_index_5_day_change: Decimal | None = None
    implied_volatility_index_rank: str | None = None
    tos_implied_volatility_index_rank: Decimal | None = None
    tw_implied_volatility_index_rank: Decimal | None = None
    tos_implied_volatility_index_rank_updated_at: datetime | None = None
    implied_volatility_index_rank_source: str | None = None
    implied_volatility_percentile: str | None = None
    implied_volatility_updated_at: datetime | None = None
    liquidity_rating: int | None = None
    updated_at: datetime
    option_expiration_implied_volatilities: (
        list[OptionExpirationImpliedVolatility] | None
    ) = None  # noqa: E501
    beta: Decimal | None = None
    corr_spy_3month: Decimal | None = None
    market_cap: Decimal
    earnings: EarningsReport | None = None
    price_earnings_ratio: Decimal | None = None
    earnings_per_share: Decimal | None = None
    dividend_rate_per_share: Decimal | None = None
    implied_volatility_30_day: Decimal | None = None
    historical_volatility_30_day: Decimal | None = None
    historical_volatility_60_day: Decimal | None = None
    historical_volatility_90_day: Decimal | None = None
    iv_hv_30_day_difference: Decimal | None = None
    beta_updated_at: datetime | None = None
    created_at: datetime | None = None
    dividend_ex_date: date | None = None
    dividend_next_date: date | None = None
    dividend_pay_date: date | None = None
    dividend_updated_at: datetime | None = None
    liquidity_value: Decimal | None = None
    liquidity_rank: Decimal | None = None
    liquidity_running_state: Liquidity | None = None
    dividend_yield: Decimal | None = None
    listed_market: str | None = None
    lendability: str | None = None
    borrow_rate: Decimal | None = None


async def a_get_market_metrics(
    session: Session, symbols: list[str]
) -> list[MarketMetricInfo]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param symbols: list of symbols to retrieve metrics for
    """
    data = await session._a_get(
        "/market-metrics", params={"symbols": ",".join(symbols)}
    )
    return [MarketMetricInfo(**i) for i in data["items"]]


def get_market_metrics(session: Session, symbols: list[str]) -> list[MarketMetricInfo]:
    """
    Retrieves market metrics for the given symbols.

    :param session: active user session to use
    :param symbols: list of symbols to retrieve metrics for
    """
    data = session._get("/market-metrics", params={"symbols": ",".join(symbols)})
    return [MarketMetricInfo(**i) for i in data["items"]]


async def a_get_dividends(session: Session, symbol: str) -> list[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for
    """
    symbol = symbol.replace("/", "%2F")
    data = await session._a_get(
        f"/market-metrics/historic-corporate-events/dividends/{symbol}"
    )
    return [DividendInfo(**i) for i in data["items"]]


def get_dividends(session: Session, symbol: str) -> list[DividendInfo]:
    """
    Retrieves dividend information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve dividend information for
    """
    symbol = symbol.replace("/", "%2F")
    data = session._get(f"/market-metrics/historic-corporate-events/dividends/{symbol}")
    return [DividendInfo(**i) for i in data["items"]]


async def a_get_earnings(
    session: Session, symbol: str, start_date: date
) -> list[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date
    """
    symbol = symbol.replace("/", "%2F")
    params = {"start-date": start_date}
    data = await session._a_get(
        (f"/market-metrics/historic-corporate-events/earnings-reports/{symbol}"),
        params=params,
    )
    return [EarningsInfo(**i) for i in data["items"]]


def get_earnings(session: Session, symbol: str, start_date: date) -> list[EarningsInfo]:
    """
    Retrieves earnings information for the given symbol.

    :param session: active user session to use
    :param symbol: symbol to retrieve earnings information for
    :param start_date: limits earnings to those on or after the given date
    """
    symbol = symbol.replace("/", "%2F")
    params = {"start-date": start_date}
    data = session._get(
        (f"/market-metrics/historic-corporate-events/earnings-reports/{symbol}"),
        params=params,
    )
    return [EarningsInfo(**i) for i in data["items"]]


async def a_get_risk_free_rate(session: Session) -> Decimal:
    """
    Retrieves the current risk-free rate.

    :param session: active user session to use
    """
    request = session.async_client.build_request(
        "GET", "/margin-requirements-public-configuration", timeout=30
    )
    del request.headers["Authorization"]
    response = await session.async_client.send(request)
    data = validate_and_parse(response)
    return Decimal(data["risk-free-rate"])


def get_risk_free_rate(session: Session) -> Decimal:
    """
    Retrieves the current risk-free rate.

    :param session: active user session to use
    """
    request = session.sync_client.build_request(
        "GET", "/margin-requirements-public-configuration", timeout=30
    )
    del request.headers["Authorization"]
    response = session.sync_client.send(request)
    data = validate_and_parse(response)
    return Decimal(data["risk-free-rate"])
