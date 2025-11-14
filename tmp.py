import asyncio
import os
from datetime import date, datetime, time

import pandas as pd

from tastytrade import Session
from tastytrade.dxfeed.candle import Candle
from tastytrade.streamer import DXLinkStreamer
from tastytrade.utils import TZ

session = Session(os.environ["TT_SECRET"], os.environ["TT_REFRESH"])


async def main():
    async with DXLinkStreamer(session) as streamer:
        start_time = datetime.combine(date(2025, 11, 7), time(9, 30), tzinfo=TZ)
        ts = round(start_time.timestamp() * 1000)
        await streamer.subscribe_candle(["DIA"], "5s", start_time=start_time)
        candles: list[Candle] = []
        async for candle in streamer.listen(Candle):
            candles.append(candle)
            if candle.time <= ts:
                break
        candles.sort(key=lambda c: c.time)
        df = pd.DataFrame([c.model_dump() for c in candles])
        df = df[["time", "open", "high", "low", "close"]]
        print(df)


if __name__ == "__main__":
    asyncio.run(main())
