from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase

import pytest
from proxy import TestCase

from tastytrade import Account, AlertStreamer, DXLinkStreamer, Session
from tastytrade.dxfeed import Candle, Quote, Trade

pytestmark = pytest.mark.anyio


async def test_account_streamer(session: Session):
    async with AlertStreamer(session) as streamer:
        await streamer.subscribe_public_watchlists()
        await streamer.subscribe_quote_alerts()
        accounts = await Account.get(session)
        await streamer.subscribe_accounts(accounts)


async def test_dxlink_streamer(session: Session):
    async with DXLinkStreamer(session) as streamer:
        subs = ["SPY", "AAPL"]
        await streamer.subscribe(Quote, subs)
        # this symbol doesn't exist
        await streamer.subscribe(Trade, ["QQQQ"])
        start_date = datetime.today() - timedelta(days=30)
        await streamer.subscribe_candle(subs, "1d", start_date)
        _ = await streamer.get_event(Candle)
        assert streamer.get_event_nowait(Candle) is not None
        assert streamer.get_event_nowait(Trade) is None
        async for _ in streamer.listen(Quote):
            break
        await streamer.unsubscribe_candle(subs[0], "1d")
        await streamer.unsubscribe(Quote, [subs[0]])
        await streamer.unsubscribe_all(Quote)


@pytest.mark.usefixtures("inject_credentials")
class TestProxy(TestCase, IsolatedAsyncioTestCase):
    async def test_streamer_with_proxy(self):
        assert self.PROXY is not None
        session = Session(
            *self.credentials,  # type: ignore
            proxy=f"http://127.0.0.1:{self.PROXY.flags.port}",
        )
        await session._refresh()
        assert await session.validate()
        async with DXLinkStreamer(session) as streamer:
            await streamer.subscribe(Quote, ["SPY"])
            _ = await streamer.get_event(Quote)
