from pydantic import BaseModel
from requests import Response


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
    return s.replace('_', '-')


class TastytradeJsonDataclass(BaseModel):
    """
    A pydantic dataclass that converts keys from snake case to dasherized
    and performs type validation and coercion.
    """
    class Config:
        alias_generator = _dasherize
        allow_population_by_field_name = True


def validate_response(response: Response) -> None:
    """
    Checks if the given code is an error; if so, raises an exception.

    :param response: response to check for errors
    """
    if response.status_code // 100 != 2:
        content = response.json()['error']
        error_message = f"{content['code']}: {content['message']}"
        errors = content.get('errors')
        if errors is not None:
            for error in errors:
                error_message += f"\n{error['code']}: {error['message']}"

        raise TastytradeError(error_message)
