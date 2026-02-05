import pytest

from tastytrade import Session
from tastytrade.search import symbol_search

pytestmark = pytest.mark.anyio


async def test_symbol_search_valid(session: Session):
    results = await symbol_search(session, "AAP")
    symbols = [s.symbol for s in results]
    assert "AAPL" in symbols


async def test_symbol_search_invalid(session: Session):
    results = await symbol_search(session, "ASDFGJKL")
    assert results == []
