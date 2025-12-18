from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any

from httpx import AsyncClient, Client
from typing_extensions import Self

from tastytrade import API_URL, API_VERSION, CERT_URL, logger
from tastytrade.utils import (
    TastytradeData,
    now_in_new_york,
    validate_and_parse,
    validate_response,
)


class Address(TastytradeData):
    """
    Dataclass containing customer address information.
    """

    city: str
    country: str
    is_domestic: bool
    is_foreign: bool
    postal_code: str
    state_region: str
    street_one: str
    street_two: str | None = None
    street_three: str | None = None


class EntityOfficer(TastytradeData):
    """
    Dataclass containing entity officer information.
    """

    id: str
    external_id: str
    first_name: str
    last_name: str
    middle_name: str
    prefix_name: str
    suffix_name: str
    address: Address
    birth_country: str
    birth_date: date
    citizenship_country: str
    email: str
    employer_name: str
    employment_status: str
    home_phone_number: str
    is_foreign: bool
    job_title: str
    marital_status: str
    mobile_phone_number: str
    number_of_dependents: int
    occupation: str
    owner_of_record: bool
    relationship_to_entity: str
    tax_number: str
    tax_number_type: str
    usa_citizenship_type: str
    visa_expiration_date: date
    visa_type: str
    work_phone_number: str


class EntitySuitability(TastytradeData):
    """
    Dataclass containing entity suitability information.
    """

    id: str
    annual_net_income: int
    covered_options_trading_experience: str
    entity_id: int
    futures_trading_experience: str
    liquid_net_worth: int
    net_worth: int
    stock_trading_experience: str
    tax_bracket: str
    uncovered_options_trading_experience: str


class CustomerAccountMarginType(TastytradeData):
    """
    Dataclass containing margin information for a customer account type.
    """

    name: str
    is_margin: bool


class CustomerAccountType(TastytradeData):
    """
    Dataclass containing information for a type of customer account.
    """

    name: str
    description: str
    is_tax_advantaged: bool
    is_publicly_available: bool
    has_multiple_owners: bool
    margin_types: list[CustomerAccountMarginType]


class CustomerEntity(TastytradeData):
    """
    Dataclass containing customer entity information.
    """

    id: str
    address: Address
    business_nature: str
    email: str
    entity_officers: list[EntityOfficer]
    entity_suitability: EntitySuitability
    entity_type: str
    foreign_institution: str
    grantor_birth_date: str
    grantor_email: str
    grantor_first_name: str
    grantor_last_name: str
    grantor_middle_name: str
    grantor_tax_number: str
    has_foreign_bank_affiliation: str
    has_foreign_institution_affiliation: str
    is_domestic: bool
    legal_name: str
    phone_number: str
    tax_number: str


class CustomerPerson(TastytradeData):
    """
    Dataclass containing customer person information.
    """

    external_id: str
    first_name: str
    last_name: str
    citizenship_country: str
    usa_citizenship_type: str
    employment_status: str
    marital_status: str
    number_of_dependents: int
    occupation: str | None = None
    middle_name: str | None = None
    prefix_name: str | None = None
    suffix_name: str | None = None
    birth_country: str | None = None
    birth_date: date | str | None = None
    visa_expiration_date: date | None = None
    visa_type: str | None = None
    employer_name: str | None = None
    job_title: str | None = None


class CustomerSuitability(TastytradeData):
    """
    Dataclass containing customer suitability information.
    """

    id: int
    annual_net_income: int
    covered_options_trading_experience: str
    employment_status: str
    futures_trading_experience: str
    liquid_net_worth: int
    marital_status: str
    net_worth: int
    number_of_dependents: int
    stock_trading_experience: str
    uncovered_options_trading_experience: str
    customer_id: str | None = None
    employer_name: str | None = None
    job_title: str | None = None
    occupation: str | None = None
    tax_bracket: str | None = None


class Customer(TastytradeData):
    """
    Dataclass containing customer information.
    """

    id: str
    first_name: str
    first_surname: str
    last_name: str
    address: Address
    customer_suitability: CustomerSuitability
    mailing_address: Address
    is_foreign: bool
    regulatory_domain: str
    usa_citizenship_type: str
    home_phone_number: str
    mobile_phone_number: str
    work_phone_number: str
    birth_date: date
    email: str
    external_id: str
    tax_number: str
    tax_number_type: str
    citizenship_country: str
    agreed_to_margining: bool
    subject_to_tax_withholding: bool
    agreed_to_terms: bool
    ext_crm_id: str
    has_industry_affiliation: bool
    has_listed_affiliation: bool
    has_political_affiliation: bool
    has_delayed_quotes: bool
    has_pending_or_approved_application: bool
    is_professional: bool
    permitted_account_types: list[CustomerAccountType]
    created_at: datetime
    identifiable_type: str
    person: CustomerPerson
    gender: str | None = None
    middle_name: str | None = None
    prefix_name: str | None = None
    second_surname: str | None = None
    suffix_name: str | None = None
    foreign_tax_number: str | None = None
    birth_country: str | None = None
    visa_expiration_date: date | None = None
    visa_type: str | None = None
    signature_of_agreement: bool | None = None
    desk_customer_id: str | None = None
    entity: CustomerEntity | None = None
    family_member_names: str | None = None
    has_institutional_assets: str | bool | None = None
    industry_affiliation_firm: str | None = None
    is_investment_adviser: bool | None = None
    listed_affiliation_symbol: str | None = None
    political_organization: str | None = None
    user_id: str | None = None


_fmt = "%Y-%m-%d %H:%M:%S%z"


class Session:
    """
    Contains a managed user login which can then be used to interact with the
    remote API.

    :param provider_secret: OAuth secret for your provider
    :param refresh_token: refresh token for the user
    :param is_test:
        whether to use the test API endpoints, default False
    :param proxy:
        if provided, all requests will be made through this proxy, as well as
        web socket connections for streamers.
    """

    def __init__(
        self,
        provider_secret: str,
        refresh_token: str,
        is_test: bool = False,
        proxy: str | None = None,
    ):
        #: Whether this is a cert or real session
        self.is_test = is_test
        #: Proxy URL to use for requests and web sockets
        self.proxy = proxy
        #: OAuth secret for your provider
        self.provider_secret = provider_secret
        #: Refresh token for the user
        self.refresh_token = refresh_token
        # The headers to use for API requests
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if not is_test:  # not accepted in sandbox
            headers["Accept-Version"] = API_VERSION
        #: httpx client for sync requests
        self.sync_client = Client(
            base_url=(CERT_URL if is_test else API_URL), headers=headers, proxy=proxy
        )
        #: httpx client for async requests
        self.async_client = AsyncClient(
            base_url=self.sync_client.base_url, headers=headers, proxy=proxy
        )
        #: expiration for streamer token
        self.streamer_expiration = now_in_new_york()
        self.refresh()

    def _streamer_refresh(self, data: Any) -> None:
        # Auth token for dxfeed websocket
        self.streamer_token = data["token"]
        # URL for dxfeed websocket
        self.dxlink_url = data["dxlink-url"]
        self.streamer_expiration = datetime.fromisoformat(
            data["expires-at"].replace("Z", "+00:00")
        )

    def refresh(self) -> None:
        """
        Refreshes the acccess token using the stored refresh token.
        Also refreshes the streamer token if necessary.
        """
        request = self.sync_client.build_request(
            "POST",
            "/oauth/token",
            json={
                "grant_type": "refresh_token",
                "client_secret": self.provider_secret,
                "refresh_token": self.refresh_token,
            },
        )
        # Don't send the Authorization header for this request
        request.headers.pop("Authorization", None)
        response = self.sync_client.send(request)
        validate_response(response)
        data = response.json()
        #: The session token used to authenticate requests
        self.session_token = data["access_token"]
        token_lifetime: int = data.get("expires_in", 900)
        #: expiration for session token
        self.session_expiration = now_in_new_york() + timedelta(seconds=token_lifetime)
        logger.debug(f"Refreshed token, expires in {token_lifetime}ms")
        auth_headers = {"Authorization": f"Bearer {self.session_token}"}
        # update the httpx clients with the new token
        self.sync_client.headers.update(auth_headers)
        self.async_client.headers.update(auth_headers)
        # update the streamer token if necessary
        if not self.is_test and self.streamer_expiration < self.session_expiration:
            data = self._get("/api-quote-tokens")
            self._streamer_refresh(data)

    async def a_refresh(self) -> None:
        """
        Refreshes the acccess token using the stored refresh token.
        Also refreshes the streamer token if necessary.
        """
        request = self.async_client.build_request(
            "POST",
            "/oauth/token",
            json={
                "grant_type": "refresh_token",
                "client_secret": self.provider_secret,
                "refresh_token": self.refresh_token,
            },
        )
        # Don't send the Authorization header for this request
        request.headers.pop("Authorization", None)
        response = await self.async_client.send(request)
        validate_response(response)
        data = response.json()
        # update the relevant tokens
        self.session_token = data["access_token"]
        token_lifetime: int = data.get("expires_in", 900)
        self.session_expiration = now_in_new_york() + timedelta(token_lifetime)
        logger.debug(f"Refreshed token, expires in {token_lifetime}ms")
        auth_headers = {"Authorization": f"Bearer {self.session_token}"}
        # update the httpx clients with the new token
        self.sync_client.headers.update(auth_headers)
        self.async_client.headers.update(auth_headers)
        # update the streamer token if necessary
        if not self.is_test and self.streamer_expiration < self.session_expiration:
            # Pull streamer tokens and urls
            data = await self._a_get("/api-quote-tokens")
            self._streamer_refresh(data)

    async def a_get_customer(self) -> Customer:
        """
        Gets the customer dict from the API.
        """
        data = await self._a_get("/customers/me")
        return Customer(**data)

    def get_customer(self) -> Customer:
        """
        Gets the customer dict from the API.
        """
        data = self._get("/customers/me")
        return Customer(**data)

    async def a_validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.
        """
        response = await self.async_client.post("/sessions/validate")
        return response.status_code // 100 == 2

    def validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.
        """
        response = self.sync_client.post("/sessions/validate")
        return response.status_code // 100 == 2

    def serialize(self) -> str:
        """
        Serializes the session to a string, useful for storing
        a session for later use.
        Could be used with pickle, Redis, etc.
        """
        attrs = self.__dict__.copy()
        del attrs["async_client"]
        del attrs["sync_client"]
        attrs["session_expiration"] = self.session_expiration.strftime(_fmt)
        attrs["streamer_expiration"] = self.streamer_expiration.strftime(_fmt)
        attrs["headers"] = dict(self.sync_client.headers.copy())
        return json.dumps(attrs)

    @classmethod
    def deserialize(cls, serialized: str) -> Self:
        """
        Create a new Session object from a serialized string.
        """
        deserialized: dict[str, Any] = json.loads(serialized)
        headers = deserialized.pop("headers")
        self = cls.__new__(cls)
        self.__dict__ = deserialized
        base_url = CERT_URL if self.is_test else API_URL
        self.session_expiration = datetime.strptime(
            deserialized["session_expiration"], _fmt
        )
        self.streamer_expiration = datetime.strptime(
            deserialized["streamer_expiration"], _fmt
        )
        self.sync_client = Client(base_url=base_url, headers=headers, proxy=self.proxy)
        self.async_client = AsyncClient(
            base_url=base_url, headers=headers, proxy=self.proxy
        )
        return self

    async def _a_get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = await self.async_client.get(url, timeout=30, **kwargs)
        return validate_and_parse(response)

    def _get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self.sync_client.get(url, timeout=30, **kwargs)
        return validate_and_parse(response)

    async def _a_delete(self, url: str, **kwargs: Any) -> None:
        response = await self.async_client.delete(url, **kwargs)
        validate_response(response)

    def _delete(self, url: str, **kwargs: Any) -> None:
        response = self.sync_client.delete(url, **kwargs)
        validate_response(response)

    async def _a_post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = await self.async_client.post(url, **kwargs)
        return validate_and_parse(response)

    def _post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self.sync_client.post(url, **kwargs)
        return validate_and_parse(response)

    async def _a_put(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = await self.async_client.put(url, **kwargs)
        return validate_and_parse(response)

    def _put(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self.sync_client.put(url, **kwargs)
        return validate_and_parse(response)
