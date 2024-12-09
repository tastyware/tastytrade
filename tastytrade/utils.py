from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pandas_market_calendars as mcal  # type: ignore
from httpx._models import Response
from pydantic import BaseModel, ConfigDict

NYSE = mcal.get_calendar("NYSE")
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

    :return: current time as datetime
    """
    return datetime.now(TZ)


def today_in_new_york() -> date:
    """
    Gets the current date in the New York timezone.

    :return: current date
    """
    return now_in_new_york().date()


def is_market_open_on(day: Optional[date] = None) -> bool:
    """
    Returns whether the market was/is/will be open at ANY point
    during the given day.

    :param day: date to check. If not provided defaults to current NY date.

    :return: whether the market opens on given day
    """
    if not day:
        day = today_in_new_york()
    date_range = NYSE.valid_days(day, day)
    return not date_range.empty


def get_third_friday(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the month of the given date,
    or the monthly expiration associated with today's month.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    day = day.replace(day=1)
    day += timedelta(weeks=2)
    while day.weekday() != 4:  # Friday
        day += timedelta(days=1)
    return day


def get_tasty_monthly() -> date:
    """
    Gets the monthly expiration closest to 45 days from the current date.

    :return: the closest to 45 DTE monthly expiration
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


def get_future_fx_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the FX futures: /6E, /6A, etc.
    As far as I can tell, these expire on the first Friday prior to the second
    Wednesday.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    day = day.replace(day=1)
    day += timedelta(weeks=1)
    while day.weekday() != 2:  # Wednesday
        day += timedelta(days=1)
    while day.weekday() != 4:  # Friday
        day -= timedelta(days=1)
    return day


def get_future_treasury_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the treasury futures: /ZN,
    /ZB, etc. According to CME, these expire the Friday before the 2nd last
    business day of the month. If this is not a business day, they expire 1
    business day prior.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-2] - timedelta(days=1)
    while itr.weekday() != 4:  # Friday
        itr -= timedelta(days=1)
    if itr in valid_range:
        return itr
    return itr - timedelta(days=1)


def get_future_metal_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the metals futures: /GC, /SI,
    etc. According to CME, these expire on the 4th last business day of the
    month, unless that day occurs on a Friday or the day before a holiday, in
    which case they expire on the prior business day.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-4]
    next_day = itr + timedelta(days=1)
    if itr.weekday() == 4 or next_day not in valid_range:
        return valid_range[-5]
    return itr


def get_future_grain_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the grain futures: /ZC, /ZW,
    etc. According to CME, these expire on the Friday which precedes, by at
    least 2 business days, the last business day of the month.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    itr = valid_range[-3]
    while itr.weekday() != 4:  # Friday
        itr -= timedelta(days=1)
    return itr


def get_future_oil_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the WTI oil futures: /CL and
    /MCL. According to CME, these expire 6 business days before the 25th day
    of the month, unless the 25th day is not a business day, in which case
    they expire 7 business days prior to the 25th day of the month.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    last_day = day.replace(day=25)
    first_day = last_day.replace(day=1)
    valid_range = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    return valid_range[-7]


def get_future_index_monthly(day: Optional[date] = None) -> date:
    """
    Gets the monthly expiration associated with the index futures: /ES, /RTY,
    /NQ, etc. According to CME, these expire on the last business day of the
    month.

    :param day: date to check. If not provided defaults to current NY date.

    :return: the associated monthly
    """
    if not day:
        day = today_in_new_york()
    last_day = _get_last_day_of_month(day)
    first_day = last_day.replace(day=1)
    valid_range = [d.date() for d in NYSE.valid_days(first_day, last_day)]
    return valid_range[-1]


class TastytradeError(Exception):
    """
    An internal error raised by the Tastytrade API.
    """

    pass


def _dasherize(s: str) -> str:
    """
    Converts a string from snake case to dasherized.

    :param s: string to convert

    :return: dasherized string
    """
    return s.replace("_", "-")


class TastytradeJsonDataclass(BaseModel):
    """
    A pydantic dataclass that converts keys from snake case to dasherized
    and performs type validation and coercion.
    """

    model_config = ConfigDict(alias_generator=_dasherize, populate_by_name=True)


def validate_response(response: Response) -> None:
    """
    Checks if the given code is an error; if so, raises an exception.

    :param response: response to check for errors
    """
    if response.status_code // 100 != 2:
        content = response.json()["error"]
        error_message = f"{content['code']}: {content['message']}"
        errors = content.get("errors")
        if errors is not None:
            for error in errors:
                if "code" in error:
                    error_message += f"\n{error['code']}: {error['message']}"
                else:
                    error_message += f"\n{error['domain']}: {error['reason']}"

        raise TastytradeError(error_message)


def _get_sign(value: Optional[Decimal]) -> Optional[PriceEffect]:
    if not value:
        return None
    return PriceEffect.DEBIT if value < 0 else PriceEffect.CREDIT


def _set_sign_for(data: Any, properties: list[str]) -> Any:
    """
    Handles setting the sign of a number using the associated "-effect" field.

    :param data: the raw, unprocessed model object
    :param properties: the name of the number fields to set
    """
    if isinstance(data, dict):
        for property in properties:
            key = _dasherize(property)
            effect = data.get(f"{key}-effect")
            if effect == PriceEffect.DEBIT:
                data[key] = -abs(Decimal(data[key]))
    return data
