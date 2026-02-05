from datetime import date

import pytest

from tastytrade import Session
from tastytrade.metrics import (
    get_dividends,
    get_earnings,
    get_market_metrics,
    get_risk_free_rate,
)

pytestmark = pytest.mark.anyio


async def test_get_dividends(session: Session):
    await get_dividends(session, "SPY")


async def test_get_earnings(session: Session):
    await get_earnings(session, "AAPL", date.today())


async def test_get_market_metrics(session: Session):
    await get_market_metrics(session, ["SPY", "AAPL"])


async def test_get_risk_free_rate(session: Session):
    await get_risk_free_rate(session)
