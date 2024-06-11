from datetime import datetime, timedelta

import pytest

from tastytrade import Account, AlertStreamer, DXLinkStreamer
from tastytrade.dxfeed import EventType

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_account_streamer(session):
    async with AlertStreamer(session) as streamer:
        await streamer.subscribe_public_watchlists()
        await streamer.subscribe_quote_alerts()
        await streamer.subscribe_user_messages(session)
        accounts = Account.get_accounts(session)
        await streamer.subscribe_accounts(accounts)


@pytest.mark.asyncio
async def test_dxlink_streamer(session):
    async with DXLinkStreamer(session) as streamer:
        subs = ['SPY', 'AAPL']
        await streamer.subscribe(EventType.QUOTE, subs)
        # this symbol doesn't exist
        await streamer.subscribe(EventType.TRADE, ['QQQQ'])
        start_date = datetime.today() - timedelta(days=30)
        await streamer.subscribe_candle(subs, '1d', start_date)
        _ = await streamer.get_event(EventType.CANDLE)
        assert streamer.get_event_nowait(EventType.CANDLE) is not None
        assert streamer.get_event_nowait(EventType.TRADE) is None
        async for _ in streamer.listen(EventType.QUOTE):
            break
        await streamer.unsubscribe_candle(subs[0], '1d')
        await streamer.unsubscribe(EventType.QUOTE, subs[1])
