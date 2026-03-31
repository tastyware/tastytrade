import math
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any, Literal
from uuid import uuid4

from httpx import AsyncClient
from httpx_ws import HTTPXWSException

from tastytrade import PAPER_URL
from tastytrade.account import Account
from tastytrade.session import Session
from tastytrade.streamer import AlertStreamer
from tastytrade.utils import validate_response


class PaperSession(Session):
    """
    Contains a session which can be used to interact with the paper trading API.
    Note these sessions are only valid for endpoints in the Account class.

    :param api_key: user's paper API key, buy one at https://tastyware.dev/login
    """

    def __init__(self, api_key: str, **client_kwargs: Any):
        super().__init__("kyrie", "eleison", is_test=True)
        self.api_key = api_key
        self.session_expiration = math.inf
        # The headers to use for API requests
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        }
        # httpx client for async requests
        self._client = AsyncClient(base_url=PAPER_URL, headers=headers, **client_kwargs)
        client_kwargs["headers"] = headers
        self.client_kwargs = client_kwargs

    async def create_account(
        self,
        name: str,
        margin_or_cash: Literal["Cash", "Margin"] = "Margin",
        initial_deposit: int = 100_000,
    ) -> Account:
        """
        Create a new paper trading account with the given configuration.

        :param name: name for the account
        :param margin_or_cash: whether the account should be margin or cash
        :param initial_deposit: the initial balance for the new account
        """
        json = {
            "account_name": name,
            "margin_or_cash": margin_or_cash,
            "initial_deposit": initial_deposit,
        }
        data = await self._post("/accounts", json=json)
        return Account(**data)

    async def delete_account(self, account: Account) -> None:
        """
        Delete the given paper trading account along with its orders, transactions, etc.

        :param account: account to delete
        """
        params = {"account_number": account.account_number}
        await self._delete("/accounts", params=params)

    async def deposit(self, account: Account, amount: Decimal) -> None:
        """
        Deposit the given quantity of fake dollars into the paper trading account. Use
        with a negative number for withdrawals.

        :param account: account to deposit into
        :param amount: amount of money to deposit/withdraw
        """
        params = {"account_number": account.account_number, "amount": f"{amount:.2f}"}
        response = await self._client.post("/accounts/deposit", params=params)
        validate_response(response)

    @asynccontextmanager
    async def temporary_account(
        self, margin_or_cash: Literal["Cash", "Margin"] = "Margin"
    ) -> AsyncGenerator[Account, None]:
        """
        Create an account for temporary use that will be cleaned up when exiting the
        context manager. Useful for automated testing.

        :param margin_or_cash: whether the account should be margin or cash
        """
        acc = await self.create_account(uuid4().hex, margin_or_cash=margin_or_cash)
        try:
            yield acc
        finally:
            await self.delete_account(acc)


class PaperAlertStreamer(AlertStreamer):
    """
    Designed to mimic the behavior and API of :attr:`tastytrade.AlertStreamer`.
    Currently only supports listening to orders.
    """

    def __init__(self, session: PaperSession) -> None:
        super().__init__(session)
        self.base_url = PAPER_URL.replace("http", "ws") + "/notifications"

    def fail(self) -> None:
        """
        Raise an exception in the streamer that can be used to test retries.
        """
        raise HTTPXWSException("Something happened and the fake streamer broke, oh no!")
