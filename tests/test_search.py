from tastytrade.search import symbol_search


def test_symbol_search_valid(session):
    results = symbol_search(session, 'AAP')
    symbols = [s.symbol for s in results]
    assert 'AAPL' in symbols


def test_symbol_search_invalid(session):
    results = symbol_search(session, 'ASDFGJKL')
    assert results == []
