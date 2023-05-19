from pydantic import BaseModel
from requests import Response


class TastytradeError(Exception):
    """
    An internal error raised by the Tastytrade API.
    """
    pass


class TastytradeJsonDataclass(BaseModel):
    """
    A pydantic dataclass that converts keys from snake case to dasherized
    and performs type validation and coercion.
    """
    class Config:
        alias_generator = lambda s: s.replace('_', '-')


def validate_response(response: Response) -> None:
    """
    Checks if the given code is an error; if so, raises an exception.

    :param json: response to check for errors
    """
    if response.status_code // 100 != 2:
        content = response.json()['error']
        raise TastytradeError(f"{content['code']}: {content['message']}")
