import json
from dataclasses import dataclass
from typing import List

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response


@dataclass
class DestinationVenueSymbol:
    id: int
    symbol: str
    destination_venue: str
    routable: bool
    max_quantity_precision: int = None
    max_price_precision: int = None


@dataclass
class Cryptocurrency:
    id: int
    symbol: str
    instrument_type: str
    short_description: str
    description: str
    is_closing_only: bool
    active: bool
    tick_size: str
    streamer_symbol: str
    destination_venue_symbols: List[DestinationVenueSymbol]


class Instruments:
    def get_cryptocurrencies(
        self, session: Session, symbols: List[str] = None
    ) -> List[Cryptocurrency]:
        if symbols:
            symbol_params = "&".join([f"symbol[]={s}" for s in symbols])
            url = f"{session.base_url}/instruments/cryptocurrencies?{symbol_params}"
        else:
            url = f"{session.base_url}/instruments/cryptocurrencies"

        response = requests.get(url, headers=session.headers)
        validate_response(response)
        response_data = json.loads(response.content)
        cryptocurrencies_data = response_data["data"]["items"]
        cryptocurrencies = []
        for data in cryptocurrencies_data:
            data = {
                k.replace("-", "_"): v for k, v in data.items()
            }  # replace hyphens with underscores in keys
            destination_venue_symbols = [
                DestinationVenueSymbol(
                    **{k.replace("-", "_"): v for k, v in dvs.items()}
                )
                for dvs in data.pop("destination_venue_symbols")
            ]
            cryptocurrencies.append(
                Cryptocurrency(
                    destination_venue_symbols=destination_venue_symbols, **data
                )
            )
        return cryptocurrencies
