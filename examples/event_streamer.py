"""
Example usage of the EventStreamer class

NOTE: quick and dirty implementation
"""

import asyncio
import os
from datetime import datetime
from decimal import Decimal
from typing import TypeVar

import dotenv

from tastytrade.dxfeed import (
    Candle,
    Greeks,
    Profile,
    Quote,
    Summary,
    TheoPrice,
    TimeAndSale,
    Trade,
    Underlying,
)
from tastytrade.session import Session
from tastytrade.streamer import EventStreamer

dotenv.load_dotenv()

session = Session(
    provider_secret=os.getenv("TT_API_CLIENT_SECRET", ""),
    refresh_token=os.getenv("TT_REFRESH_TOKEN", ""),
)


E = TypeVar(
    "E",
    Candle,
    Greeks,
    Profile,
    Quote,
    Summary,
    TheoPrice,
    TimeAndSale,
    Trade,
    Underlying,
)


class OHLCVBar:
    def __init__(self, symbol: str, open_price: Decimal, volume: int | None, timestamp: datetime):
        self.symbol: str = symbol
        self.open: Decimal = open_price
        self.high: Decimal = open_price
        self.low: Decimal = open_price
        self.close: Decimal = open_price
        self.volume: int | None = volume
        self.tick_count: int = 1
        self.timestamp: datetime = timestamp

    def update(self, price: Decimal, volume: int | None) -> None:
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.volume = volume if volume is not None else self.volume
        self.tick_count += 1

    def __str__(self) -> str:
        return (
            f"OHLCVBar(symbol={self.symbol}, open={self.open}, high={self.high}, low={self.low},"
            f" close={self.close}, volume={self.volume}, "
            f"tick_count={self.tick_count}, timestamp={self.timestamp})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class OHLCVBars:
    def __init__(self, timeframe: str, symbol: str):
        self.ohlcv_bars: list[OHLCVBar] = []
        self.current_bar: OHLCVBar | None = None
        self.timeframe: str = timeframe
        self.symbol: str = symbol

    def update(self, event: Trade) -> None:
        ts_ms = event.time

        # --- TICK BARS ---
        if self.timeframe.endswith("t"):
            n = int(self.timeframe[:-1])  # "200t" -> 200 (also works for "1t")

            if self.current_bar is None:
                self.current_bar = OHLCVBar(self.symbol, event.price, event.size, timestamp=datetime.fromtimestamp(ts_ms / 1000))
            else:
                self.current_bar.update(event.price, event.size)

            # close AFTER update so tick_count includes this trade
            if self.current_bar.tick_count >= n:
                self.ohlcv_bars.append(self.current_bar)
                # start a new bar on next tick (or immediately if you prefer)
                self.current_bar = None
                print(self.ohlcv_bars[-1])
            return

        # --- TIME BARS (bucketed) ---
        bucket_ts = self.bucket_timestamp(ts_ms, self.timeframe)

        if self.current_bar is None:
            self.current_bar = OHLCVBar(
                self.symbol, event.price, event.size, timestamp=bucket_ts
            )
            return

        # If this tick belongs to a new time bucket, finalize old bar and start new one
        if bucket_ts != self.current_bar.timestamp:
            self.ohlcv_bars.append(self.current_bar)
            self.current_bar = OHLCVBar(
                self.symbol, event.price, event.size, timestamp=bucket_ts
            )
            print(self.ohlcv_bars[-1])
        else:
            self.current_bar.update(event.price, event.size)

    @staticmethod
    def bucket_timestamp(ts_ms: int, timeframe: str) -> datetime:
        # floor ts into the timeframe bucket so you never get two candles for the
        # same bucket
        if timeframe == "5s":
            start = (ts_ms // 5_000) * 5_000
        elif timeframe == "1m":
            start = (ts_ms // 60_000) * 60_000
        elif timeframe == "5m":
            start = (ts_ms // 300_000) * 300_000
        elif timeframe == "15m":
            start = (ts_ms // 900_000) * 900_000
        elif timeframe == "30m":
            start = (ts_ms // 1_800_000) * 1_800_000
        elif timeframe == "1h":
            start = (ts_ms // 3_600_000) * 3_600_000
        elif timeframe == "4h":
            start = (ts_ms // 14_400_000) * 14_400_000
        elif timeframe == "1d":
            start = (ts_ms // 86_400_000) * 86_400_000
        elif timeframe == "1w":
            start = (ts_ms // 604_800_000) * 604_800_000
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        return datetime.fromtimestamp(start / 1000)


ohlcv_bars_dict: dict[str, OHLCVBars] = {}


def ohlcv_bars(symbols: list[str]) -> None:
    global ohlcv_bars_list
    for symbol in symbols:
        ohlcv_bars_dict[symbol] = OHLCVBars("5s", symbol)


async def update_ohlcv_bars(trade: Trade) -> None:
    global ohlcv_bars_dict
    ohlcv_bars_dict[trade.event_symbol].update(trade)


async def handle_quote(quote: Quote) -> None:
    print(f"QUOTE: {quote}")


async def monitor_tasks(tasks: list[asyncio.Task[None]], stop_time: int) -> None:
    """
    Monitor the tasks and stop them after the given time
    """
    await asyncio.sleep(stop_time)
    for t in tasks:
        t.cancel()


async def main() -> None:
    quote_streamer = EventStreamer(session, ["SPY"], Quote, handle_quote)
    symbols = ["SPY", "AAPL"]
    ohlcv_bars(symbols=symbols)  # initialize the ohlcv bars in a global dictionary

    ohlcv_bars_streamers = [EventStreamer(session, [symbol], Trade, update_ohlcv_bars) for symbol in symbols]

    tasks: list[asyncio.Task[None]] = []
    tasks.append(asyncio.create_task(quote_streamer.start()))
    for t in ohlcv_bars_streamers:
        tasks.append(asyncio.create_task(t.start()))

    try:
        await asyncio.gather(*tasks, monitor_tasks(tasks, 20))
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
