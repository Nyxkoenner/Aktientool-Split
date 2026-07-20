from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

import pandas as pd

from stock_explorer.providers.base import MarketDataProvider
from stock_explorer.providers.fx import FxProvider
from stock_explorer.services.portfolio_simulation_service import PortfolioSimulationService


class FakeMarketProvider(MarketDataProvider):
    name = "fake"

    def download_price_histories(
        self, tickers: tuple[str, ...], period: str = "5y"
    ) -> dict[str, pd.DataFrame]:
        index = pd.date_range("2025-01-01", periods=370, freq="D")
        return {
            ticker: pd.DataFrame({"Close": pd.Series(range(100, 470), index=index)}) for ticker in tickers
        }

    def get_info(self, ticker: str, wanted_keys: Iterable[str]) -> dict[str, Any]:
        return {key: None for key in wanted_keys}

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        return pd.DataFrame({"date": [pd.Timestamp("2025-06-01")], "amount": [1.0]})

    def fx_to_eur(self, currency: str) -> Optional[float]:
        return 1.0


class FakeFxProvider(FxProvider):
    name = "fake-fx"

    def to_eur(self, currency: str) -> Optional[float]:
        return 1.0


def test_service_runs_transaction_and_benchmark_simulation(tmp_path: Path) -> None:
    transactions = pd.DataFrame(
        [
            {
                "date": "2025-01-01",
                "type": "DEPOSIT",
                "cash_amount": 1000,
                "currency": "EUR",
            },
            {
                "date": "2025-01-02",
                "ticker_yahoo": "AAA",
                "type": "BUY",
                "shares": 5,
                "price": 101,
                "currency": "EUR",
                "fees": 1,
            },
        ]
    )
    path = tmp_path / "transactions.csv"
    transactions.to_csv(path, index=False)
    service = PortfolioSimulationService(FakeMarketProvider(), FakeFxProvider())
    bundle = service.run(
        transactions_path=path,
        market_data=pd.DataFrame([{"ticker_yahoo": "AAA", "currency": "EUR", "last_price": 469.0}]),
        existing_histories={},
        benchmark_ticker="BENCH",
    )
    assert bundle.result.final_value > bundle.result.net_contributions
    assert bundle.result.dividends_received > 0
    assert bundle.benchmark is not None
    assert bundle.benchmark.final_value > 0
