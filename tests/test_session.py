from tastytrade import Session


def test_get_customer(session):
    session.get_customer()


async def test_get_customer_async(session):
    await session.a_get_customer()


def test_get_2fa_info(session):
    session.get_2fa_info()


async def test_get_2fa_info_async(session):
    await session.a_get_2fa_info()


def test_destroy(credentials):
    session = Session(*credentials)
    session.destroy()


async def test_destroy_async(credentials):
    session = Session(*credentials)
    await session.a_destroy()
