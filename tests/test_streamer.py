import asyncio
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


async def reconnect_alerts(streamer: AlertStreamer, ref: dict[str, bool]):
    await streamer.subscribe_quote_alerts()
    ref["test"] = True


async def test_account_streamer_reconnect(session):
    ref = {}
    streamer = await AlertStreamer(
        session, reconnect_args=(ref,), reconnect_fn=reconnect_alerts
    )
    await streamer.subscribe_public_watchlists()
    await streamer.subscribe_user_messages(session)
    accounts = Account.get_accounts(session)
    await streamer.subscribe_accounts(accounts)
    await streamer._websocket.close()  # type: ignore
    await asyncio.sleep(3)
    assert "test" in ref
    streamer.close()


async def reconnect_trades(streamer: DXLinkStreamer):
    await streamer.subscribe(Trade, ["SPX"])


async def test_dxlink_streamer_reconnect(session):
    streamer = await DXLinkStreamer(session, reconnect_fn=reconnect_trades)
    await streamer.subscribe(Quote, ["SPY"])
    _ = await streamer.get_event(Quote)
    await streamer._websocket.close()
    await asyncio.sleep(3)
    trade = await streamer.get_event(Trade)
    assert trade.event_symbol == "SPX"
    streamer.close()
