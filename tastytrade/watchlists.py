from typing import Any, Self, overload

from tastytrade.order import InstrumentType
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
    async def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def get(
        cls,
        session: Session,
        name: str | None = None,
    ) -> Self | list[Self]:
        """
        Fetches a list of all Tastytrade public pairs watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.
        """
        if name:
            data = await session._get(f"/pairs-watchlists/{name}")
            return cls(**data)
        data = await session._get("/pairs-watchlists")
        return [cls(**i) for i in data["items"]]


class Watchlist(TastytradeData):
    name: str
    watchlist_entries: list[dict[str, Any]] | None = None
    group_name: str = "default"
    order_index: int = 9999


class PublicWatchlist(Watchlist):
    """
    Dataclass that contains symbols from a public watchlist.
    """

    @overload
    @classmethod
    async def get(
        cls, session: Session, *, counts_only: bool = False
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def get(
        cls,
        session: Session,
        name: str | None = None,
        *,
        counts_only: bool = False,
    ) -> Self | list[Self]:
        """
        Fetches a list of all Tastytrade public watchlists, or a specific one if
        a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        :param counts_only: whether to only fetch the counts of the watchlists.
        """
        if name:
            data = await session._get(f"/public-watchlists/{name}")
            return cls(**data)
        data = await session._get(
            "/public-watchlists", params={"counts-only": counts_only}
        )
        return [cls(**i) for i in data["items"]]


class PrivateWatchlist(Watchlist):
    """
    Dataclass that contains a private watchlist object, with functions to
    update, publish, modify and remove watchlists.
    """

    @overload
    @classmethod
    async def get(cls, session: Session) -> list[Self]: ...

    @overload
    @classmethod
    async def get(cls, session: Session, name: str) -> Self: ...

    @classmethod
    async def get(
        cls,
        session: Session,
        name: str | None = None,
    ) -> Self | list[Self]:
        """
        Fetches the user's private watchlists, or a specific one if a name is provided.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.
        """
        if name:
            data = await session._get(f"/watchlists/{name}")
            return cls(**data)
        data = await session._get("/watchlists")
        return [cls(**i) for i in data["items"]]

    @classmethod
    async def remove(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        await session._delete(f"/watchlists/{name}")

    async def upload(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        await session._post("/watchlists", json=self.model_dump(by_alias=True))

    async def update(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        await session._put(
            f"/watchlists/{self.name}", json=self.model_dump(by_alias=True)
        )

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
