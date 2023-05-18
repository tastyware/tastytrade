import calendar
from datetime import date, datetime, timedelta
from typing import Any

from requests import Response


class TastytradeError(Exception):
    """
    An internal error raised by the Tastytrade API.
    """

    pass


def validate_response(response: Response) -> None:
    """
    Checks if the given code is an error; if so, raises an exception.

    :param json: response to check for errors
    """
    if response.status_code // 100 != 2:
        content = response.json()['error']
        raise TastytradeError(f"{content['code']}: {content['message']}")


def get_third_friday(d: date) -> date:
    """
    Returns the date of the monthly option in the same month as the given date, unless that date has already passed, in which case the next month's monthly will be returned.

    :param d: input date from which to calculate the date of the monthly

    :return: closest monthly to current date that hasn't already passed
    """
    s = date(d.year, d.month, 15)
    candidate = s + timedelta(days=(calendar.FRIDAY - s.weekday()) % 7)

    # This month's third friday passed
    if candidate < d:
        candidate += timedelta(weeks=4)
        if candidate.day < 15:
            candidate += timedelta(weeks=1)

    return candidate


def snakeify(json: dict[str, Any]) -> dict[str, Any]:
    """
    Converts all keys in the given dictionary to snake case.

    :param json: dictionary to convert

    :return: dictionary with snake case keys
    """
    return {key.replace('-', '_'): value for key, value in json.items()}


def desnakeify(json: dict[str, Any]) -> dict[str, Any]:
    """
    Converts all keys in the given dictionary from underscores to dashes.

    :param json: dictionary to convert

    :return: dictionary with dashed keys
    """
    return {key.replace('_', '-'): value for key, value in json.items()}


def datetime_from_tastydatetime(tastydatetime: str) -> datetime:
    """
    Converts a Tastytrade datetime string to a datetime object.

    :param tastydatetime: datetime string to convert

    :return: datetime object
    """
    return datetime.strptime(tastydatetime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
