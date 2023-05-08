import aiohttp

from tastytrade import API_URL
from tastytrade.session import Session


class Watchlist(object):
    """Watchlist Class"""

    def __init__(self):
        """init"""
        self.name = None
        self.group_name = None
        self.securities = {}

    @classmethod
    def from_list(cls, data: list):
        """From List

        Class Factory

        Notes:
            There is an instability issue with Tastyworks API.  Hence
            the need to catch an exceptions.  Special symbols don't have
            instrument types at all.

            For stability & accessibility, all instrument types are returned
            as 'instrument_type'.

        Args:
            data (list):   List of dict objects containing symbol &
                           instrument_type

        Returns:
            Watchlist:  Instance of Watchlist()
        """
        inst = cls()
        for item in data:
            try:
                inst.securities[item['symbol']] = {
                    'instrument_type': item['instrument-type']
                }
            except KeyError:
                try:
                    inst.securities[item['symbol']] = {
                        'instrument_type': item['instrument_type']
                    }
                except KeyError:
                    inst.securities[item['symbol']] = {
                        'instrument_type': None
                    }
        return inst

    def __str__(self):
        """String Representation"""
        return str(self.__dict__)


class WatchlistGroup(object):
    """WatchlistGroup Class"""

    def __init__(self):
        """init"""
        self.watchlists = {}

    def __iter__(self):
        """Iterator"""
        return iter(self.watchlists)

    def __getitem__(self, item):
        """Subscriptor"""
        return self.watchlists[item]

    def __repr__(self):
        """Object Representation"""
        return str(self.watchlists)

    def __str__(self):
        """String Representation"""
        return str(list(self.watchlists.keys()))

    @classmethod
    async def get_watchlists(cls, session: Session, public: bool = True):
        """Get Watchlists

        Class Factory

        Retrieves a watchlist group (either public or private).

        Notes:
            Not all Watchlist's have group names.

        Args:
            session (TastyAPISession): A TastyAPISession object
            public (bool): Retrive public or private watchlists

        Returns:
            WatchlistGroup: Instance of WatchlistGroup()
        """
        url = f'{API_URL}/public-watchlists' if public else f'{API_URL}/watchlists'

        async with aiohttp.request('GET', url, headers=session.headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise Exception(f'Failed retrieving watchlists, Response status: {resp.status}; message: {data["error"]["message"]}')

        data = data['data']['items']
        inst = cls()
        for entry in data:
            list_data = entry['watchlist-entries']
            wlist = Watchlist.from_list(list_data)
            wlist.name = entry['name']
            try:
                wlist.group_name = entry['group-name']
            except KeyError:
                pass
            inst.watchlists[wlist.name] = wlist

        return inst
