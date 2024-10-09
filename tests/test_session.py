from tastytrade import Session


def test_get_customer(session):
    session.get_customer()


async def test_get_customer_async(session):
    await session.a_get_customer()


def test_get_2fa_info(session):
    session.get_2fa_info()


async def test_get_2fa_info_async(session):
    await session.a_get_2fa_info()


def test_destroy(get_cert_credentials):
    usr, pwd = get_cert_credentials
    session = Session(usr, pwd, is_test=True)
    session.destroy()


async def test_destroy_async(get_cert_credentials):
    usr, pwd = get_cert_credentials
    session = Session(usr, pwd, is_test=True)
    await session.a_destroy()
