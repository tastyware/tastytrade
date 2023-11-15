import pytest
import pytest_asyncio

from tastytrade import Account, AccountStreamer

pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def streamer(session):
    streamer = await AccountStreamer.create(session)
    yield streamer
    streamer.close()


@pytest.mark.asyncio
async def test_subscribe_all(session, streamer):
    await streamer.public_watchlists_subscribe()
    await streamer.quote_alerts_subscribe()
    await streamer.user_message_subscribe(session)
    accounts = Account.get_accounts(session)
    await streamer.account_subscribe(accounts)
