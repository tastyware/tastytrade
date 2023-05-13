from dataclasses import dataclass
from typing import Any

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response


@dataclass
class PairsWatchlist:
    name: str
    pairs_equations: list[dict[str, Any]]
    order_index: int

    @classmethod
    def from_dict(cls, json: dict[str, Any]):
        """
        Creates a PairsWatchlist object from the Tastytrade 'PairsWatchlist' object in JSON format.
        """
        snake_json = {key.replace('-', '_'): value for key, value in json.items()}
        return cls(**snake_json)

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
        watchlists = [cls.from_dict(w) for w in watchlists]

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

        return cls.from_dict(response.json()['data'])


@dataclass
class Watchlist:
    name: str
    watchlist_entries: list[dict[str, Any]]
    order_index: int
    group_name: str = 'default'

    @classmethod
    def from_dict(cls, json: dict[str, Any]):
        """
        Creates a Watchlist object from the Tastytrade 'Watchlist' object in JSON format.
        """
        snake_json = {key.replace('-', '_'): value for key, value in json.items()}
        return cls(**snake_json)

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
        watchlists = [cls.from_dict(w) for w in watchlists]

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

        return cls.from_dict(response.json()['data'])

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
        watchlists = [cls.from_dict(w) for w in watchlists]

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

        return cls.from_dict(response.json()['data'])
    
    @classmethod
    def remove_private_watchlist(cls, session: Session, name: str) -> None:
        """
        Deletes the named private watchlist.

        :param session: the session to use for the request.
        :param name: the name of the watchlist to delete.
        """
        response = requests.delete(f'{session.base_url}/watchlists/{name}', headers=session.headers)
        validate_response(response)

    def create_private_watchlist(self, session: Session) -> None:
        """
        Creates a private remote watchlist identical to this local one.

        :param session: the session to use for the request.
        """
        json = {key.replace('_', '-'): value for key, value in self.__dict__.items()}
        print(json)
        response = requests.post(
            f'{session.base_url}/watchlists',
            headers=session.headers,
            json=json
        )
        validate_response(response)
