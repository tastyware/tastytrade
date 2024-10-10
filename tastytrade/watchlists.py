from typing import Any, Dict, List, Optional

from typing_extensions import Self

from tastytrade.instruments import InstrumentType
from tastytrade.session import Session
from tastytrade.utils import TastytradeJsonDataclass


class Pair(TastytradeJsonDataclass):
    """
    Dataclass that represents a specific pair in a pairs watchlist.
    """

    left_action: str
    left_symbol: str
    left_quantity: int
    right_action: str
    right_symbol: str
    right_quantity: int


class PairsWatchlist(TastytradeJsonDataclass):
    """
    Dataclass that represents a pairs watchlist object.
    """

    name: str
    order_index: int
    pairs_equations: List[Pair]

    @classmethod
    async def a_get_pairs_watchlists(cls, session: Session) -> List[Self]:
        """
        Fetches a list of all Tastytrade public pairs watchlists.

        :param session: the session to use for the request.
        """
        data = await session._a_get("/pairs-watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    def get_pairs_watchlists(cls, session: Session) -> List[Self]:
        """
        Fetches a list of all Tastytrade public pairs watchlists.

        :param session: the session to use for the request.
        """
        data = session._get("/pairs-watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    async def a_get_pairs_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a Tastytrade public pairs watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.
        """
        data = await session._a_get(f"/pairs-watchlists/{name}")
        return cls(**data)

    @classmethod
    def get_pairs_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a Tastytrade public pairs watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.
        """
        data = session._get(f"/pairs-watchlists/{name}")
        return cls(**data)


class Watchlist(TastytradeJsonDataclass):
    """
    Dataclass that represents a watchlist object (public or private),
    with functions to update, publish, modify and remove watchlists.
    """

    name: str
    watchlist_entries: Optional[List[Dict[str, Any]]] = None
    group_name: str = "default"
    order_index: int = 9999

    @classmethod
    async def a_get_public_watchlists(
        cls, session: Session, counts_only: bool = False
    ) -> List[Self]:
        """
        Fetches a list of all Tastytrade public watchlists.

        :param session: the session to use for the request.
        :param counts_only: whether to only fetch the counts of the watchlists.
        """
        data = await session._a_get(
            "/public-watchlists", params={"counts-only": counts_only}
        )
        return [cls(**i) for i in data["items"]]

    @classmethod
    def get_public_watchlists(
        cls, session: Session, counts_only: bool = False
    ) -> List[Self]:
        """
        Fetches a list of all Tastytrade public watchlists.

        :param session: the session to use for the request.
        :param counts_only: whether to only fetch the counts of the watchlists.
        """
        data = session._get("/public-watchlists", params={"counts-only": counts_only})
        return [cls(**i) for i in data["items"]]

    @classmethod
    async def a_get_public_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a Tastytrade public watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        data = await session._a_get(f"/public-watchlists/{name}")
        return cls(**data)

    @classmethod
    def get_public_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a Tastytrade public watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        data = session._get(f"/public-watchlists/{name}")
        return cls(**data)

    @classmethod
    async def a_get_private_watchlists(cls, session: Session) -> List[Self]:
        """
        Fetches a the user's private watchlists.

        :param session: the session to use for the request.
        """
        data = await session._a_get("/watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    def get_private_watchlists(cls, session: Session) -> List[Self]:
        """
        Fetches a the user's private watchlists.

        :param session: the session to use for the request.
        """
        data = session._get("/watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    async def a_get_private_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a user's watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        data = await session._a_get(f"/watchlists/{name}")
        return cls(**data)

    @classmethod
    def get_private_watchlist(cls, session: Session, name: str) -> Self:
        """
        Fetches a user's watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        data = session._get(f"/watchlists/{name}")
        return cls(**data)

    @classmethod
    async def a_remove_private_watchlist(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        await session._a_delete(f"/watchlists/{name}")

    @classmethod
    def remove_private_watchlist(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        session._delete(f"/watchlists/{name}")

    async def a_upload_private_watchlist(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        await session._a_post("/watchlists", json=self.model_dump(by_alias=True))

    def upload_private_watchlist(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        session._post("/watchlists", json=self.model_dump(by_alias=True))

    async def a_update_private_watchlist(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        await session._a_put(
            f"/watchlists/{self.name}", json=self.model_dump(by_alias=True)
        )

    def update_private_watchlist(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        session._put(f"/watchlists/{self.name}", json=self.model_dump(by_alias=True))

    def add_symbol(self, symbol: str, instrument_type: InstrumentType) -> None:
        """
        Adds a symbol to the watchlist.
        """
        if self.watchlist_entries is None:
            self.watchlist_entries = []
        self.watchlist_entries.append(
            {"symbol": symbol, "instrument-type": instrument_type}
        )

    def remove_symbol(self, symbol: str, instrument_type: InstrumentType) -> None:
        """
        Removes a symbol from the watchlist.
        """
        if self.watchlist_entries is not None:
            self.watchlist_entries.remove(
                {"symbol": symbol, "instrument-type": instrument_type}
            )
