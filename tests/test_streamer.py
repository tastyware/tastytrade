from datetime import datetime, timedelta

from tastytrade import Account, AlertStreamer, DXLinkStreamer
from tastytrade.dxfeed import Candle, Quote, Trade


async def test_account_streamer(session):
    async with AlertStreamer(session) as streamer:
        await streamer.subscribe_public_watchlists()
        await streamer.subscribe_quote_alerts()
        await streamer.subscribe_user_messages(session)
        accounts = Account.get_accounts(session)
        await streamer.subscribe_accounts(accounts)


async def test_dxlink_streamer(session):
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
