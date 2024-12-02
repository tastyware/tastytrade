from datetime import date, datetime
from typing import Any, Optional, Union

import httpx

from tastytrade import API_URL, CERT_URL
from tastytrade.utils import TastytradeError, TastytradeJsonDataclass, validate_response


class Address(TastytradeJsonDataclass):
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
    street_two: Optional[str] = None
    street_three: Optional[str] = None


class EntityOfficer(TastytradeJsonDataclass):
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


class EntitySuitability(TastytradeJsonDataclass):
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


class CustomerAccountMarginType(TastytradeJsonDataclass):
    """
    Dataclass containing margin information for a customer account type.
    """

    name: str
    is_margin: bool


class CustomerAccountType(TastytradeJsonDataclass):
    """
    Dataclass containing information for a type of customer account.
    """

    name: str
    description: str
    is_tax_advantaged: bool
    is_publicly_available: bool
    has_multiple_owners: bool
    margin_types: list[CustomerAccountMarginType]


class CustomerEntity(TastytradeJsonDataclass):
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


class CustomerPerson(TastytradeJsonDataclass):
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
    occupation: Optional[str] = None
    middle_name: Optional[str] = None
    prefix_name: Optional[str] = None
    suffix_name: Optional[str] = None
    birth_country: Optional[str] = None
    birth_date: Optional[Union[date, str]] = None
    visa_expiration_date: Optional[date] = None
    visa_type: Optional[str] = None
    employer_name: Optional[str] = None
    job_title: Optional[str] = None


class CustomerSuitability(TastytradeJsonDataclass):
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
    customer_id: Optional[str] = None
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    occupation: Optional[str] = None
    tax_bracket: Optional[str] = None


class Customer(TastytradeJsonDataclass):
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
    gender: Optional[str] = None
    middle_name: Optional[str] = None
    prefix_name: Optional[str] = None
    second_surname: Optional[str] = None
    suffix_name: Optional[str] = None
    foreign_tax_number: Optional[str] = None
    birth_country: Optional[str] = None
    visa_expiration_date: Optional[date] = None
    visa_type: Optional[str] = None
    signature_of_agreement: Optional[bool] = None
    desk_customer_id: Optional[str] = None
    entity: Optional[CustomerEntity] = None
    family_member_names: Optional[str] = None
    has_institutional_assets: Optional[str] = None
    industry_affiliation_firm: Optional[str] = None
    is_investment_adviser: Optional[bool] = None
    listed_affiliation_symbol: Optional[str] = None
    political_organization: Optional[str] = None
    user_id: Optional[str] = None


class TwoFactorInfo(TastytradeJsonDataclass):
    """
    Dataclass containing information about two-factor authentication.
    """

    is_active: bool
    type: Optional[str] = None


class User(TastytradeJsonDataclass):
    """
    Dataclass containing information about a Tastytrade user.
    """

    email: str
    external_id: str
    is_confirmed: bool
    username: str
    name: Optional[str] = None
    nickname: Optional[str] = None


class Session:
    """
    Contains a local user login which can then be used to interact with the
    remote API.

    :param login: tastytrade username or email
    :param remember_me:
        whether or not to create a remember token to use instead of a password
    :param password:
        tastytrade password to login; if absent, remember token is required
    :param remember_token:
        previously generated token; if absent, password is required
    :param is_test:
        whether to use the test API endpoints, default False
    :param two_factor_authentication:
        if two factor authentication is enabled, this is the code sent to the
        user's device
    :param dxfeed_tos_compliant:
        whether to use the dxfeed TOS-compliant API endpoint for the streamer
    """

    def __init__(
        self,
        login: str,
        password: Optional[str] = None,
        remember_me: bool = False,
        remember_token: Optional[str] = None,
        is_test: bool = False,
        two_factor_authentication: Optional[str] = None,
        dxfeed_tos_compliant: bool = False,
    ):
        body = {"login": login, "remember-me": remember_me}
        if password is not None:
            body["password"] = password
        elif remember_token is not None:
            body["remember-token"] = remember_token
        else:
            raise TastytradeError(
                "You must provide a password or remember token to log in."
            )
        #: Whether this is a cert or real session
        self.is_test = is_test
        # The headers to use for API requests
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        #: httpx client for sync requests
        self.sync_client = httpx.Client(
            base_url=(CERT_URL if is_test else API_URL), headers=headers
        )
        if two_factor_authentication is not None:
            response = self.sync_client.post(
                "/sessions",
                json=body,
                headers={"X-Tastyworks-OTP": two_factor_authentication},
            )
        else:
            response = self.sync_client.post("/sessions", json=body)
        validate_response(response)  # throws exception if not 200

        json = response.json()
        #: The user dict returned by the API; contains basic user information
        self.user = User(**json["data"]["user"])
        #: The session token used to authenticate requests
        self.session_token = json["data"]["session-token"]
        #: A single-use token which can be used to login without a password
        self.remember_token = json["data"].get("remember-token")
        self.sync_client.headers.update({"Authorization": self.session_token})
        self.validate()
        #: httpx client for async requests
        self.async_client = httpx.AsyncClient(
            base_url=self.sync_client.base_url, headers=self.sync_client.headers.copy()
        )

        # Pull streamer tokens and urls
        url = (
            "/api-quote-tokens"
            if dxfeed_tos_compliant or is_test
            else "/quote-streamer-tokens"
        )
        data = self._get(url)
        #: Auth token for dxfeed websocket
        self.streamer_token = data["token"]
        #: URL for dxfeed websocket
        self.dxlink_url = data["dxlink-url"]

    async def _a_get(self, url, **kwargs) -> dict[str, Any]:
        response = await self.async_client.get(url, timeout=30, **kwargs)
        return self._validate_and_parse(response)

    def _get(self, url, **kwargs) -> dict[str, Any]:
        response = self.sync_client.get(url, timeout=30, **kwargs)
        return self._validate_and_parse(response)

    async def _a_delete(self, url, **kwargs) -> None:
        response = await self.async_client.delete(url, **kwargs)
        validate_response(response)

    def _delete(self, url, **kwargs) -> None:
        response = self.sync_client.delete(url, **kwargs)
        validate_response(response)

    async def _a_post(self, url, **kwargs) -> dict[str, Any]:
        response = await self.async_client.post(url, **kwargs)
        return self._validate_and_parse(response)

    def _post(self, url, **kwargs) -> dict[str, Any]:
        response = self.sync_client.post(url, **kwargs)
        return self._validate_and_parse(response)

    async def _a_put(self, url, **kwargs) -> dict[str, Any]:
        response = await self.async_client.put(url, **kwargs)
        return self._validate_and_parse(response)

    def _put(self, url, **kwargs) -> dict[str, Any]:
        response = self.sync_client.put(url, **kwargs)
        return self._validate_and_parse(response)

    def _validate_and_parse(self, response: httpx._models.Response) -> dict[str, Any]:
        validate_response(response)
        return response.json()["data"]

    async def a_validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.

        :return: True if the session is valid and False otherwise.
        """
        response = await self.async_client.post("/sessions/validate")
        return response.status_code // 100 == 2

    def validate(self) -> bool:
        """
        Validates the current session by sending a request to the API.

        :return: True if the session is valid and False otherwise.
        """
        response = self.sync_client.post("/sessions/validate")
        return response.status_code // 100 == 2

    async def a_destroy(self) -> None:
        """
        Sends a API request to log out of the existing session. This will
        invalidate the current session token and login.
        """
        await self._a_delete("/sessions")

    def destroy(self) -> None:
        """
        Sends a API request to log out of the existing session. This will
        invalidate the current session token and login.
        """
        self._delete("/sessions")

    async def a_get_customer(self) -> Customer:
        """
        Gets the customer dict from the API.

        :return: a Tastytrade 'Customer' object in JSON format.
        """
        data = await self._a_get("/customers/me")
        return Customer(**data)

    def get_customer(self) -> Customer:
        """
        Gets the customer dict from the API.

        :return: a Tastytrade 'Customer' object in JSON format.
        """
        data = self._get("/customers/me")
        return Customer(**data)

    async def a_get_2fa_info(self) -> TwoFactorInfo:
        """
        Gets the 2FA info for the current user.
        """
        data = await self._a_get("/users/me/two-factor-method")
        return TwoFactorInfo(**data)

    def get_2fa_info(self) -> TwoFactorInfo:
        """
        Gets the 2FA info for the current user.
        """
        data = self._get("/users/me/two-factor-method")
        return TwoFactorInfo(**data)
