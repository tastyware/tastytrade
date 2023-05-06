from dataclasses import dataclass

import requests

from tastytrade import API_URL


@dataclass
class TradingAccount:
    account_number: str
    external_id: str
    is_margin: bool
    is_closed: bool
    account_type_name: str
    nickname: str
    opened_at: str

    @classmethod
    def get_custormers(cls):
        """
        Gets a full customer resource
        """

    @classmethod
    def get_full_customer_account(cls, session, account_number):
        """
        Get a full customer account resource.
        """
        url = f"{API_URL}/customers/me/accounts/{account_number}"

        response = requests.get(url, headers=session.get_request_headers())

        if response.status_code == 200:
            account_data = response.json()
            print("Account data:", account_data)
        else:
            print(f"Error: {response.status_code} - {response.text}")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Parses a TradingAccount object from a dict.
        """
        new_data = {
            "is_margin": True if data["margin-or-cash"] == "Margin" else False,
            "account_number": data["account-number"],
            "external_id": data["external-id"],
            "is_closed": True if data["is-closed"] else False,
            "account_type_name": data["account-type-name"],
            "nickname": data["nickname"],
            "opened_at": data["opened-at"],
        }

        return TradingAccount(**new_data)

    @classmethod
    def get_accounts(cls, session, include_closed=False) -> list:
        """
        Gets all trading accounts from the Tastyworks platform.
        By default excludes closed accounts, but these can be added
        by passing include_closed=True.

        Args:
            session (Session): An active and logged-in session object against which to query.

        Returns:
            list (TradingAccount): A list of trading accounts.
        """
        url = f"{API_URL}/customers/me/accounts"
        res = []

        response = requests.get(url, headers=session.get_request_headers())
        if response.status_code != 200:
            raise Exception("Could not get trading accounts info from Tastyworks...")
        data = response.json()["data"]

        for entry in data["items"]:
            if entry["authority-level"] != "owner":
                continue
            acct_data = entry["account"]
            if not include_closed and acct_data["is-closed"]:
                continue
            acct = TradingAccount.from_dict(acct_data)
            res.append(acct)

        return res
