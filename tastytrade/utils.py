from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from json import JSONDecodeError
from typing import Any, Type, TypeVar, cast
from zoneinfo import ZoneInfo

from httpx import AsyncClient, Client, Response
from pandas import Timestamp
from pandas_market_calendars import get_calendar  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict

from tastytrade import logger

NYSE: Any = get_calendar("NYSE")
TZ = ZoneInfo("US/Eastern")


class PriceEffect(str, Enum):
    """
    This is an :class:`~enum.Enum` that shows the sign of a price effect, since
    Tastytrade is apparently against negative numbers.
    """

    CREDIT = "Credit"
    DEBIT = "Debit"
    NONE = "None"


def now_in_new_york() -> datetime:
    """
    Gets the current time in the New York timezone.
    """
    return datetime.now(TZ)


def today_in_new_york() -> date:
    """
    Gets the current date in the New York timezone.
    """
    return now_in_new_york().date()


def is_market_open_now() -> bool:
    """
    Check if the market is currently open.
    """
    today = today_in_new_york()
    sched = NYSE.schedule(start_date=today, end_date=today)
    if sched.empty:
        # Closed full day (weekend or holiday)
        return False

    # Use iloc[0] since schedule has only one row for a single day
    market_open: Timestamp = sched.iloc[0]["market_open"]
    market_close: Timestamp = sched.iloc[0]["market_close"]
    return market_open <= now_in_new_york() < market_close


def is_market_open_on(day: date | None = None) -> bool:
    """
    Returns whether the market was/is/will be open at ANY point
    during the given day.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = day or today_in_new_york()
    date_range = NYSE.valid_days(day, day)
    return not date_range.empty


def get_third_friday(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the month of the given date,
    or the monthly expiration associated with today's month.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = (day or today_in_new_york()).replace(day=1) + timedelta(weeks=2)
    while day.weekday() != 4:  # Friday
        day += timedelta(days=1)
    return day


def get_tasty_monthly() -> date:
    """
    Gets the monthly expiration closest to 45 days from the current date.
    """
    day = today_in_new_york()
    exp1 = get_third_friday(day + timedelta(weeks=4))
    exp2 = get_third_friday(day + timedelta(weeks=8))
    day45 = day + timedelta(days=45)
    return exp1 if day45 - exp1 < exp2 - day45 else exp2


def _get_last_day_of_month(day: date) -> date:
    if day.month == 12:
        last = day.replace(day=1, month=1, year=day.year + 1)
    else:
        last = day.replace(day=1, month=day.month + 1)
    return last - timedelta(days=1)


def get_future_fx_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the FX futures: /6E, /6A, etc.
    As far as I can tell, these expire on the first Friday prior to the second
    Wednesday.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = (day or today_in_new_york()).replace(day=1) + timedelta(weeks=1)
    while day.weekday() != 2:  # Wednesday
        day += timedelta(days=1)
    while day.weekday() != 4:  # Friday
        day -= timedelta(days=1)
    return day


def get_future_treasury_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the treasury futures: /ZN,
    /ZB, etc. According to CME, these expire the Friday before the 2nd last
    business day of the month. If this is not a business day, they expire 1
    business day prior.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = day or today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range: list[date] = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-2] - timedelta(days=1)
    while itr.weekday() != 4:  # Friday
        itr -= timedelta(days=1)
    if itr in valid_range:
        return itr
    return itr - timedelta(days=1)


def get_future_metal_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the metals futures: /GC, /SI,
    etc. According to CME, these expire on the 4th last business day of the
    month, unless that day occurs on a Friday or the day before a holiday, in
    which case they expire on the prior business day.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = day or today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range: list[date] = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-4]
    next_day = itr + timedelta(days=1)
    if itr.weekday() == 4 or next_day not in valid_range:
        return valid_range[-5]
    return itr


def get_future_grain_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the grain futures: /ZC, /ZW,
    etc. According to CME, these expire on the Friday which precedes, by at
    least 2 business days, the last business day of the month.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = day or today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range: list[date] = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-3]
    while itr.weekday() != 4:  # Friday
        itr -= timedelta(days=1)
    return itr


def get_future_oil_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the WTI oil futures: /CL and
    /MCL. According to CME, these expire 6 business days before the 25th day
    of the month, unless the 25th day is not a business day, in which case
    they expire 7 business days prior to the 25th day of the month.

    :param day: date to check. If not provided defaults to current NY date.
    """
    last_day = (day or today_in_new_york()).replace(day=25)
    first_day = last_day.replace(day=1)
    valid_range: list[date] = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    return valid_range[-7]


def get_future_index_monthly(day: date | None = None) -> date:
    """
    Gets the monthly expiration associated with the index futures: /ES, /RTY,
    /NQ, etc. According to CME, these expire on the last business day of the
    month.

    :param day: date to check. If not provided defaults to current NY date.
    """
    day = day or today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range: list[date] = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    return valid_range[-1]


class TastytradeError(Exception):
    """
    An internal error raised by the Tastytrade SDK.
    """

    pass


def _dasherize(s: str) -> str:
    """
    Converts a string from snake case to dasherized.

    :param s: string to convert
    """
    return s.replace("_", "-")


class TastytradeData(BaseModel):
    """
    A pydantic dataclass that converts keys from snake case to dasherized
    and performs type validation and coercion.
    """

    model_config = ConfigDict(alias_generator=_dasherize, populate_by_name=True)

    def __str__(self) -> str:
        return " ".join(f"{a}={v!r}" for a, v in self.__repr_args__() if v)

    def __repr__(self) -> str:
        return f"{self.__repr_name__()}({str(self)})"  # type: ignore


def validate_response(response: Response) -> None:
    """
    Checks if the given code is an error; if so, raises an exception.

    :param response: response to check for errors
    """
    if response.status_code // 100 != 2:
        try:
            json: dict[str, Any] = response.json()
        except JSONDecodeError as e:
            raise TastytradeError(f"Couldn't parse response: {response.text}") from e
        if not (content := json.get("error")):
            raise TastytradeError(f"Couldn't parse response: {json}")
        errors = content.get("errors") or [content]
        message = ""
        for error in errors:
            if "code" in error and "message" in error:
                message += f"{error['code']}: {error['message']}\n"
            elif "domain" in error and "reason" in error:
                message += f"{error['domain']}: {error['reason']}\n"
            else:
                logger.debug(f"Unknown error type: {error}")

        raise TastytradeError(message)


def validate_and_parse(response: Response) -> dict[str, Any]:
    """
    Checks if the given code is an error; if so, raises an exception.
    Then, returns the JSON payload.

    :param response: response to check for errors
    """
    validate_response(response)
    json = response.json()
    if not (data := json.get("data")):
        raise TastytradeError(f"No data present in response: {json}")
    return cast(dict[str, Any], data)


def get_sign(value: Decimal | None) -> PriceEffect | None:
    """
    Get a PriceEffect for a signed value.

    :param value: value to check
    """
    if not value:
        return None
    return PriceEffect.DEBIT if value < 0 else PriceEffect.CREDIT


def set_sign_for(data: Any, properties: list[str]) -> Any:
    """
    Handles setting the sign of a number using the associated "-effect" field.

    :param data: the raw, unprocessed model object
    :param properties: the name of the number fields to set
    """
    if isinstance(data, dict):
        data = cast(dict[str, Any], data)
        for property in properties:
            key = _dasherize(property)
            if data.get(f"{key}-effect") == PriceEffect.DEBIT:
                data[key] = -abs(Decimal(data[key]))
    return data


T = TypeVar("T", bound=TastytradeData)


def paginate(
    client: Client, model: Type[T], url: str, params: dict[str, Any]
) -> list[T]:
    """
    Helper for paginated endpoints. Excepts params to have at least `page-offset` and
    `per-page` parameters.
    If `params["page-offset"]` is None, iterates over all results; otherwise, gets a
    specific page.

    :param client: the httpx client for making request
    :param model: the TastytradeData model for results
    :param url: the endpoint to use
    :param params: parameters for request
    """
    res: list[T] = []
    # if a specific page is provided, we just get that page;
    # otherwise, we loop through all pages
    paginate = False
    if params["page-offset"] is None:
        params["page-offset"] = 0
        paginate = True
    params = {k: v for k, v in params.items() if v is not None}
    # loop through pages and get all transactions
    while True:
        response = client.get(url, params=params)
        validate_response(response)
        json = response.json()
        res.extend([model(**i) for i in json["data"]["items"]])
        # handle pagination
        pagination = json.get("pagination")
        if (
            not pagination
            or not paginate
            or pagination["page-offset"] >= pagination["total-pages"] - 1
        ):
            break
        params["page-offset"] += 1
    return res


async def a_paginate(
    client: AsyncClient, model: Type[T], url: str, params: dict[str, Any]
) -> list[T]:
    """
    Helper for paginated endpoints. Excepts params to have at least `page-offset` and
    `per-page` parameters.
    If `params["page-offset"]` is None, iterates over all results; otherwise, gets a
    specific page.

    :param client: the httpx client for making request
    :param model: the TastytradeData model for results
    :param url: the endpoint to use
    :param params: parameters for request
    """
    res: list[T] = []
    # if a specific page is provided, we just get that page;
    # otherwise, we loop through all pages
    paginate = False
    if params["page-offset"] is None:
        params["page-offset"] = 0
        paginate = True
    params = {k: v for k, v in params.items() if v is not None}
    # loop through pages and get all transactions
    while True:
        response = await client.get(url, params=params)
        validate_response(response)
        json = response.json()
        res.extend([model(**i) for i in json["data"]["items"]])
        # handle pagination
        pagination = json.get("pagination")
        if (
            not pagination
            or not paginate
            or pagination["page-offset"] >= pagination["total-pages"] - 1
        ):
            break
        params["page-offset"] += 1
    return res
