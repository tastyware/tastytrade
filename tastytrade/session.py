from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any, AsyncGenerator, Self, TypeVar

from anyio import AsyncContextManagerMixin, Lock
from httpx import AsyncClient

from tastytrade import API_URL, API_VERSION, CERT_URL, logger
from tastytrade.utils import (
    TastytradeData,
    validate_and_parse,
    validate_response,
)

T = TypeVar("T", bound=TastytradeData)


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
    first_surname: str | None = None
    last_name: str
    address: Address
    customer_suitability: CustomerSuitability | None = None
    mailing_address: Address
    is_foreign: bool
    regulatory_domain: str | None = None
    usa_citizenship_type: str
    home_phone_number: str | None = None
    mobile_phone_number: str
    work_phone_number: str | None = None
    birth_date: date
    email: str
    external_id: str | None = None
    tax_number: str | None = None
    tax_number_type: str
    citizenship_country: str | None = None
    agreed_to_margining: bool | None = None
    subject_to_tax_withholding: bool
    agreed_to_terms: bool | None = None
    ext_crm_id: str | None = None
    has_industry_affiliation: bool
    has_listed_affiliation: bool
    has_political_affiliation: bool
    has_delayed_quotes: bool
    has_pending_or_approved_application: bool
    is_professional: bool
    permitted_account_types: list[CustomerAccountType]
    created_at: datetime
    identifiable_type: str | None = None
    person: CustomerPerson | None = None
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


class Session(AsyncContextManagerMixin):
    """
    Contains a managed user login which can then be used to interact with the
    remote API.

    Prefer using with its async context manager to ensure proper cleanup.

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
        #: timestamp that the session will expire
        self.session_expiration = 0.0
        #: token used for authentication
        self.session_token = "kyrieeleison"
        # httpx client for all requests
        self._client = AsyncClient(
            base_url=(CERT_URL if is_test else API_URL), headers=headers, proxy=proxy
        )
        self._lock = Lock()

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with self._client:
            yield self

    async def get_customer(self) -> Customer:
        """
        Gets the customer dict from the API.
        """
        data = await self._get("/customers/me")
        return Customer(**data)

    async def validate(self) -> bool:
        """
        Check if the current session is valid by sending a request to the API.
        """
        response = await self._client.post("/sessions/validate")
        return response.status_code // 100 == 2

    def serialize(self) -> str:
        """
        Serializes the session to a string, useful for storing a session for later use.
        Could be used with pickle, Redis, etc.
        """
        attrs = self.__dict__.copy()
        del attrs["_client"]
        del attrs["_lock"]
        return json.dumps(attrs)

    @classmethod
    def deserialize(cls, serialized: str) -> Self:
        """
        Create a new Session object from a serialized string.
        """
        deserialized: dict[str, Any] = json.loads(serialized)
        self = cls(
            provider_secret=deserialized["provider_secret"],
            refresh_token=deserialized["refresh_token"],
            is_test=deserialized["is_test"],
            proxy=deserialized["proxy"],
        )
        self.session_expiration = deserialized["session_expiration"]
        self.session_token = deserialized["session_token"]
        auth_headers = {"Authorization": f"Bearer {self.session_token}"}
        self._client.headers.update(auth_headers)
        return self

    async def _refresh(self) -> None:
        # only refresh if needed; use 60 second buffer
        if time.time() < self.session_expiration - 60:
            return
        async with self._lock:
            if time.time() < self.session_expiration - 60:
                return
            request = self._client.build_request(
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
            response = await self._client.send(request)
            validate_response(response)
            data = response.json()
            # update the relevant tokens
            self.session_token = data["access_token"]
            token_lifetime: int = data.get("expires_in", 900)
            self.session_expiration = time.time() + token_lifetime
            logger.debug(f"Refreshed token, expires in {token_lifetime}s")
            auth_headers = {"Authorization": f"Bearer {self.session_token}"}
            # update the httpx client with the new token
            self._client.headers.update(auth_headers)

    async def _get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        await self._refresh()
        response = await self._client.get(url, **kwargs)
        return validate_and_parse(response)

    async def _delete(self, url: str, **kwargs: Any) -> None:
        await self._refresh()
        response = await self._client.delete(url, **kwargs)
        validate_response(response)

    async def _post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        await self._refresh()
        response = await self._client.post(url, **kwargs)
        return validate_and_parse(response)

    async def _put(self, url: str, **kwargs: Any) -> dict[str, Any]:
        await self._refresh()
        response = await self._client.put(url, **kwargs)
        return validate_and_parse(response)

    async def _paginate(
        self, model: type[T], url: str, params: dict[str, Any]
    ) -> list[T]:
        # Helper for paginated endpoints. Excepts params to have at least `page-offset`
        # and `per-page` parameters. If `params["page-offset"]` is None, iterates over
        # all results; otherwise, gets a specific page.
        res: list[T] = []
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if params["page-offset"] is None:
            params["page-offset"] = 0
            paginate = True
        params = {k: v for k, v in params.items() if v is not None}
        await self._refresh()
        # loop through pages and get all transactions
        while True:
            response = await self._client.get(url, params=params)
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
