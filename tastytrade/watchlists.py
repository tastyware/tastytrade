from dataclasses import dataclass
from typing import Any

import requests

from tastytrade.session import Session
from tastytrade.utils import desnakeify, snakeify, validate_response


@dataclass
class PairsWatchlist:
    name: str
    pairs_equations: list[dict[str, Any]]
    order_index: int

    @classmethod
    def get_pairs_watchlists(cls, session: Session) -> list['PairsWatchlist']:
        """
        Fetches a list of all Tastytrade public pairs watchlists.

        :param session: the session to use for the request.

        :return: a list of :class:`PairsWatchlist` objects.
        """
        response = requests.get(f'{session.base_url}/pairs-watchlists', headers=session.headers)
        validate_response(response)
        watchlists = response.json()['data']['items']
        watchlists = [cls(**snakeify(w)) for w in watchlists]

        return watchlists

    @classmethod
    def get_pairs_watchlist(cls, session: Session, name: str) -> 'PairsWatchlist':
        """
        Fetches a Tastytrade public pairs watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the pairs watchlist to fetch.

        :return: a :class:`PairsWatchlist` object.
        """
        response = requests.get(f'{session.base_url}/pairs-watchlists/{name}', headers=session.headers)
        validate_response(response)

        data = response.json()['data']

        return cls.from_dict(**snakeify(data))


@dataclass
class Watchlist:
    name: str
    watchlist_entries: list[dict[str, Any]]
    order_index: int
    group_name: str = 'default'

    @classmethod
    def create_empty(cls, name: str):
        """
        Creates an empty watchlist with the given name.
        """
        return cls(name=name, watchlist_entries=[], order_index=9999)

    @classmethod
    def get_public_watchlists(cls, session: Session, counts_only: bool = False) -> list['Watchlist']:
        """
        Fetches a list of all Tastytrade public watchlists.

        :param session: the session to use for the request.
        :param counts_only: whether to only fetch the counts of the watchlists.

        :return: a list of :class:`Watchlist` objects.
        """
        response = requests.get(
            f'{session.base_url}/public-watchlists',
            headers=session.headers,
            params={'counts-only': counts_only}
        )
        validate_response(response)
        watchlists = response.json()['data']['items']
        print(watchlists)
        watchlists = [cls(**snakeify(w)) for w in watchlists]

        return watchlists

    @classmethod
    def get_public_watchlist(cls, session: Session, name: str) -> 'Watchlist':
        """
        Fetches a Tastytrade public watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.

        :return: a :class:`Watchlist` object.
        """
        response = requests.get(f'{session.base_url}/public-watchlists/{name}', headers=session.headers)
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))

    @classmethod
    def get_private_watchlists(cls, session: Session) -> list['Watchlist']:
        """
        Fetches a the user's private watchlists.

        :param session: the session to use for the request.

        :return: a list of :class:`Watchlist` objects.
        """
        response = requests.get(f'{session.base_url}/watchlists', headers=session.headers)
        validate_response(response)
        watchlists = response.json()['data']['items']
        watchlists = [cls(**snakeify(w)) for w in watchlists]

        return watchlists

    @classmethod
    def get_private_watchlist(cls, session: Session, name: str) -> 'Watchlist':
        """
        Fetches a user's watchlist by name.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to fetch.

        :return: a :class:`Watchlist` object.
        """
        response = requests.get(f'{session.base_url}/watchlists/{name}', headers=session.headers)
        validate_response(response)

        data = response.json()['data']

        return cls(**snakeify(data))

    @classmethod
    def remove_private_watchlist(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        response = requests.delete(f'{session.base_url}/watchlists/{name}', headers=session.headers)
        validate_response(response)

    def upload_private_watchlist(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        json = desnakeify(self.__dict__)
        response = requests.post(
            f'{session.base_url}/watchlists',
            headers=session.headers,
            json=json
        )
        validate_response(response)

    def update_private_watchlist(self, session: Session) -> None:
        """
        Updates the existing private remote watchlist.

        :param session: the session to use for the request.
        """
        response = requests.put(
            f'{session.base_url}/watchlists/{self.name}',
            headers=session.headers,
            json=desnakeify(self.__dict__)
        )
        validate_response(response)

    def add_symbol(self, symbol: str, instrument_type: str) -> None:
        """
        Adds a symbol to the watchlist.
        """
        self.watchlist_entries.append({'symbol': symbol, 'instrument-type': instrument_type})

    def remove_symbol(self, symbol: str, instrument_type: str) -> None:
        """
        Removes a symbol from the watchlist.
        """
        self.watchlist_entries.remove({'symbol': symbol, 'instrument-type': instrument_type})
