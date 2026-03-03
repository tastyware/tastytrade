import json

import pytest

from tastytrade import Session

pytestmark = pytest.mark.anyio


async def test_get_customer(session: Session):
    await session.get_customer()


def test_serialize_deserialize(session: Session):
    # No client_kwargs
    data = session.serialize()
    obj = Session.deserialize(data)
    assert set(obj.__dict__.keys()) == set(session.__dict__.keys())
    assert obj.client_kwargs == session.client_kwargs
    # Simulate legacy serialized payloads that didn't include client_kwargs.
    legacy_payload = json.loads(data)
    del legacy_payload["client_kwargs"]
    legacy_obj = Session.deserialize(json.dumps(legacy_payload))
    assert legacy_obj.client_kwargs == {}
    # With timeout client_kwargs
    session_with_kwargs = Session(timeout=10.0)
    data_with_kwargs = session_with_kwargs.serialize()
    obj_with_kwargs = Session.deserialize(data_with_kwargs)
    assert set(obj_with_kwargs.__dict__.keys()) == set(
        session_with_kwargs.__dict__.keys()
    )
    assert obj_with_kwargs.client_kwargs == session_with_kwargs.client_kwargs
