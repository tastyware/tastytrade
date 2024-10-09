from tastytrade.search import a_symbol_search, symbol_search


async def test_symbol_search_valid_async(session):
    results = await a_symbol_search(session, "AAP")
    symbols = [s.symbol for s in results]
    assert "AAPL" in symbols


async def test_symbol_search_invalid_async(session):
    results = await a_symbol_search(session, "ASDFGJKL")
    assert results == []


def test_symbol_search_valid(session):
    results = symbol_search(session, "AAP")
    symbols = [s.symbol for s in results]
    assert "AAPL" in symbols


def test_symbol_search_invalid(session):
    results = symbol_search(session, "ASDFGJKL")
    assert results == []
