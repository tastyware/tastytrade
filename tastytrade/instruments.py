import json
from typing import List

import requests

from tastytrade.session import Session


class Instruments:
    def get_cryptocurrencies(
        self, session: Session, symbols: List[str] = None
    ) -> List[dict]:
        if symbols:
            symbol_params = "&".join([f"symbol[]={s}" for s in symbols])
            url = f"{session.base_url}/instruments/cryptocurrencies?{symbol_params}"
        else:
            url = f"{session.base_url}/instruments/cryptocurrencies"

        response = requests.get(url, headers=session.headers)
        if response.status_code == 200:
            response_data = json.loads(response.content)
            cryptocurrencies = response_data["data"]["items"]
            return cryptocurrencies
        else:
            raise Exception(
                f"Error getting cryptocurrencies: {response.status_code} - {response.content}"
            )
