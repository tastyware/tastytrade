import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import AsyncGenerator, Literal, Optional

import httpx
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

from tastytrade import BACKTEST_URL
from tastytrade.session import Session
from tastytrade.utils import (
    TastytradeError,
    validate_response,
)


class BacktestData(BaseModel):
    """
    Dataclass for converting backtest JSON naming conventions to snake case.
    """

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class BacktestEntry(BacktestData):
    """
    Dataclass of parameters for backtest trade entry.
    """

    use_exact_DTE: bool = Field(default=True, serialization_alias="useExactDTE")
    maximum_active_trials: Optional[int] = None
    maximum_active_trials_behavior: Optional[Literal["close oldest", "don't enter"]] = (
        None
    )
    frequency: str = "every day"


class BacktestExit(BacktestData):
    """
    Dataclass of parameters for backtest trade exit.
    """

    after_days_in_trade: Optional[int] = None
    stop_loss_percentage: Optional[int] = None
    take_profit_percentage: Optional[int] = None
    at_days_to_expiration: Optional[int] = None


class BacktestLeg(BacktestData):
    """
    Dataclass of parameters for placing legs of backtest trades.
    Leg delta must be a multiple of 5.
    """

    days_until_expiration: int = 45
    delta: int = 15
    direction: Literal["buy", "sell"] = "sell"
    quantity: int = 1
    side: Literal["call", "put"] = "call"


class Backtest(BacktestData):
    """
    Dataclass of configuration options for a backtest.
    """

    symbol: str
    entry_conditions: BacktestEntry
    exit_conditions: BacktestExit
    legs: list[BacktestLeg]
    start_date: date
    end_date: date = date(2024, 7, 31)
    status: str = "pending"


class BacktestSnapshot(BacktestData):
    """
    Dataclass containing a snapshot in time during the backtest.
    """

    date_time: datetime
    profit_loss: Decimal
    normalized_underlying_price: Optional[Decimal] = None
    underlying_price: Optional[Decimal] = None


class BacktestTrial(BacktestData):
    """
    Dataclass containing information on trades placed during the backtest.
    """

    close_date_time: datetime
    open_date_time: datetime
    profit_loss: Decimal


class BacktestParameters(BacktestData):
    """
    Dataclass containing valid start/end dates for a symbol.
    """

    symbol: str
    start_date: date
    end_date: date


class BacktestStatistics(BaseModel):
    """
    Dataclass containing statistics on the overall performance of a backtest.
    """

    class Config:
        populate_by_name = True

    avg_bp_per_trade: Decimal = Field(validation_alias="Avg. BPR per trade")
    avg_daily_pnl_change: Decimal = Field(validation_alias="Avg. daily change in PNL")
    avg_daily_net_liq_change: Decimal = Field(
        validation_alias="Avg. daily change in net liq"
    )
    avg_days_in_trade: Decimal = Field(validation_alias="Avg. days in trade")
    avg_premium: Decimal = Field(validation_alias="Avg. premium")
    avg_profit_loss_per_trade: Decimal = Field(
        validation_alias="Avg. profit/loss per trade"
    )
    avg_return_per_trade: Decimal = Field(validation_alias="Avg. return per trade")
    highest_profit: Decimal = Field(validation_alias="Highest profit")
    loss_percentage: Decimal = Field(validation_alias="Loss percentage")
    losses: int = Field(validation_alias="Losses")
    max_drawdown: Decimal = Field(validation_alias="Max drawdown")
    number_of_trades: int = Field(validation_alias="Number of trades")
    premium_capture_rate: Decimal = Field(validation_alias="Premium capture rate")
    return_on_used_capital: Decimal = Field(validation_alias="Return on used capital")
    total_fees: Decimal = Field(validation_alias="Total fees")
    total_premium: Decimal = Field(validation_alias="Total premium")
    total_profit_loss: Decimal = Field(validation_alias="Total profit/loss")
    used_capital: Decimal = Field(validation_alias="Used capital")
    win_percentage: Decimal = Field(validation_alias="Win percentage")
    wins: int = Field(validation_alias="Wins")
    worst_loss: Decimal = Field(validation_alias="Worst loss")


class BacktestResults(BacktestData):
    """
    Dataclass containing partial or finished results of a backtest.
    """

    snapshots: Optional[list[BacktestSnapshot]]
    statistics: Optional[BacktestStatistics]
    trials: Optional[list[BacktestTrial]]


class BacktestResponse(Backtest):
    """
    Dataclass containing a backtest and associated information.
    """

    created_at: datetime
    id: str
    results: BacktestResults
    eta: Optional[int] = None
    progress: Optional[Decimal] = None


class BacktestSession:
    """
    Class for creating a backtesting session which can be reused for multiple backtests.

    Example usage::

        from tastytrade import BacktestSession, Backtest
        from tqdm.asyncio import tqdm  # progress bar

        backtest = Backtest(...)
        backtest_session = BacktestSession(session)
        results = [r async for r in tqdm(backtest_session.run(backtest))]
        print(results[-1])

    """

    def __init__(self, session: Session):
        if session.is_test:
            raise TastytradeError("Certification sessions can't run backtests!")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # Pull backtest token
        response = httpx.post(
            f"{BACKTEST_URL}/sessions",
            json={"tastytradeToken": session.session_token},
        )
        validate_response(response)
        # Token used for backtesting
        backtest_token = response.json()["token"]
        headers["Authorization"] = f"Bearer {backtest_token}"
        self.client = httpx.AsyncClient(base_url=BACKTEST_URL, headers=headers)

    async def run(self, backtest: Backtest) -> AsyncGenerator[BacktestResponse, None]:
        """
        Run the given backtest and yield results progresively.

        :param backtest: configuration for the backtest
        """
        json = backtest.model_dump_json(by_alias=True, exclude_none=True)
        res = await self.client.post("/backtests", data=json)  # type: ignore
        validate_response(res)
        results = BacktestResponse(**res.json())
        while results.status != "completed":
            yield results
            await asyncio.sleep(0.5)
            res = await self.client.get(f"/backtests/{results.id}")
            validate_response(res)
            results = BacktestResponse(**res.json())
        yield results

    async def cancel(self, backtest_id: str) -> bool:
        """
        Cancel the running backtest with the given ID.

        :param backtest_id: ID of the backtest to cancel
        """
        res = await self.client.post(f"/backtests/{backtest_id}/cancel")
        return res.status_code // 100 == 2

    async def delete(self) -> bool:
        """
        Delete the active backtesting session.
        """
        res = await self.client.delete("/sessions")
        return res.status_code // 100 == 2

    async def get(self, backtest_id: str) -> BacktestResponse:
        """
        Fetch a specific past backtest by ID.
        """
        res = await self.client.get(f"/backtests/{backtest_id}")
        validate_response(res)
        return BacktestResponse(**res.json())

    async def available_parameters(self) -> list[BacktestParameters]:
        """
        Get a list of available symbols for backtesting, as well as valid testing dates
        for each symbol.
        """
        res = await self.client.get("/backtests/const/available-dates")
        validate_response(res)
        return [BacktestParameters(**i) for i in res.json()]
