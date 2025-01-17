from tastytrade import Session


def test_get_customer(session: Session):
    session.get_customer()


async def test_get_customer_async(session: Session):
    await session.a_get_customer()


def test_get_2fa_info(session: Session):
    session.get_2fa_info()


async def test_get_2fa_info_async(session: Session):
    await session.a_get_2fa_info()


def test_destroy(credentials: tuple[str, str]):
    session = Session(*credentials)
    session.destroy()


async def test_destroy_async(credentials: tuple[str, str]):
    session = Session(*credentials)
    await session.a_destroy()


def test_serialize_deserialize(session: Session):
    data = session.serialize()
    obj = Session.deserialize(data)
    assert set(obj.__dict__.keys()) == set(session.__dict__.keys())
