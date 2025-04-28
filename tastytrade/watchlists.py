from typing import Any, Optional, Union, overload

from typing_extensions import Self

from tastytrade.instruments import InstrumentType
from tastytrade.session import Session
from tastytrade.utils import TastytradeData


class Pair(TastytradeData):
    """
    Dataclass that represents a specific pair in a pairs watchlist.
    """

    left_action: str
    left_symbol: str
    left_quantity: int
    right_action: str
    right_symbol: str
    right_quantity: int


class PairsWatchlist(TastytradeData):
    """
    Dataclass that represents a pairs watchlist object.
    """

    name: str
    order_index: int
    pairs_equations: list[Pair]

    @overload
    @classmethod
    async def a_get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        name: Optional[str] = None,
    ) -> Union[Self, list[Self]]:
        """
        Fetches a list of all Tastytrade public pairs watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.
        """
        if name:
            data = await session._a_get(f"/pairs-watchlists/{name}")
            return cls(**data)
        data = await session._a_get("/pairs-watchlists")
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        name: Optional[str] = None,
    ) -> Union[Self, list[Self]]:
        """
        Fetches a list of all Tastytrade public pairs watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.
        """
        if name:
            data = session._get(f"/pairs-watchlists/{name}")
            return cls(**data)
        data = session._get("/pairs-watchlists")
        return [cls(**i) for i in data["items"]]


class Watchlist(TastytradeData):
    name: str
    watchlist_entries: Optional[list[dict[str, Any]]] = None
    group_name: str = "default"
    order_index: int = 9999


class PublicWatchlist(Watchlist):
    """
    Dataclass that contains symbols from a public watchlist.
    """

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, *, counts_only: bool = False
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        name: Optional[str] = None,
        *,
        counts_only: bool = False,
    ) -> Union[Self, list[Self]]:
        """
        Fetches a list of all Tastytrade public watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        :param counts_only: whether to only fetch the counts of the watchlists.
        """
        if name:
            data = await session._a_get(f"/public-watchlists/{name}")
            return cls(**data)
        data = await session._a_get(
            "/public-watchlists", params={"counts-only": counts_only}
        )
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session, *, counts_only: bool = False) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        name: Optional[str] = None,
        *,
        counts_only: bool = False,
    ) -> Union[Self, list[Self]]:
        """
        Fetches a list of all Tastytrade public watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        :param counts_only: whether to only fetch the counts of the watchlists.
        """
        if name:
            data = session._get(f"/public-watchlists/{name}")
            return cls(**data)
        data = session._get("/public-watchlists", params={"counts-only": counts_only})
        return [cls(**i) for i in data["items"]]


class PrivateWatchlist(Watchlist):
    """
    Dataclass that contains a private watchlist object, with functions to
    update, publish, modify and remove watchlists.
    """

    @overload
    @classmethod
    async def a_get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        name: Optional[str] = None,
    ) -> Union[Self, list[Self]]:
        """
        Fetches the user's private watchlists, or a specific one if a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        if name:
            data = await session._a_get(f"/watchlists/{name}")
            return cls(**data)
        data = await session._a_get("/watchlists")
        return [cls(**i) for i in data["items"]]

    @overload
    @classmethod
    def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        name: Optional[str] = None,
    ) -> Union[Self, list[Self]]:
        """
        Fetches the user's private watchlists, or a specific one if a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        if name:
            data = session._get(f"/watchlists/{name}")
            return cls(**data)
        data = session._get("/watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    async def a_remove(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        await session._a_delete(f"/watchlists/{name}")

    @classmethod
    def remove(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        session._delete(f"/watchlists/{name}")

    async def a_upload(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        await session._a_post("/watchlists", json=self.model_dump(by_alias=True))

    def upload(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        session._post("/watchlists", json=self.model_dump(by_alias=True))

    async def a_update(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        await session._a_put(
            f"/watchlists/{self.name}", json=self.model_dump(by_alias=True)
        )

    def update(self, session: Session) -> None:
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
