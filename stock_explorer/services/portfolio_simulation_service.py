from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import pandas as pd

from stock_explorer.domain.portfolio_ledger import (
    BenchmarkSimulationResult,
    LedgerSimulationResult,
    normalize_transactions,
    simulate_benchmark_with_flows,
    simulate_transaction_ledger,
)
from stock_explorer.providers.base import MarketDataProvider
from stock_explorer.providers.fx import FxProvider


@dataclass(frozen=True)
class PortfolioSimulationBundle:
    result: LedgerSimulationResult
    transactions: pd.DataFrame
    benchmark: BenchmarkSimulationResult | None
    benchmark_ticker: str | None
    currencies: Mapping[str, str]


def _price_series(history: pd.DataFrame) -> pd.Series | None:
    if history is None or history.empty:
        return None
    for column in ("Adj Close", "Close", "Kurs"):
        if column in history.columns:
            values = pd.to_numeric(history[column], errors="coerce").dropna()
            if not values.empty:
                values.index = pd.to_datetime(values.index, errors="coerce")
                if getattr(values.index, "tz", None) is not None:
                    values.index = values.index.tz_localize(None)
                return values.sort_index()
    return None


class PortfolioSimulationService:
    def __init__(self, market_provider: MarketDataProvider, fx_provider: FxProvider) -> None:
        self.market_provider = market_provider
        self.fx_provider = fx_provider

    @staticmethod
    def read_transactions(path: Path) -> pd.DataFrame:
        if not path.exists():
            return normalize_transactions(pd.DataFrame())
        try:
            frame = pd.read_csv(path)
        except Exception as error:
            raise RuntimeError(f"Could not read transaction ledger: {error}") from error
        return normalize_transactions(frame)

    def _histories(
        self,
        tickers: tuple[str, ...],
        existing_histories: Mapping[str, pd.DataFrame],
        first_transaction: pd.Timestamp,
    ) -> dict[str, pd.DataFrame]:
        histories = {ticker: existing_histories.get(ticker, pd.DataFrame()).copy() for ticker in tickers}
        refresh: list[str] = []
        for ticker, frame in histories.items():
            series = _price_series(frame)
            if series is None or series.index.min() > first_transaction:
                refresh.append(ticker)
        if refresh:
            histories.update(self.market_provider.download_price_histories(tuple(refresh), period="max"))
        return histories

    @staticmethod
    def _currency_map(
        transactions: pd.DataFrame,
        market_data: pd.DataFrame,
        base_currency: str,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        if market_data is not None and not market_data.empty:
            if {"ticker_yahoo", "currency"}.issubset(market_data.columns):
                result.update(
                    market_data.dropna(subset=["ticker_yahoo"])
                    .drop_duplicates("ticker_yahoo")
                    .set_index("ticker_yahoo")["currency"]
                    .fillna(base_currency)
                    .astype(str)
                    .to_dict()
                )
        for ticker, group in transactions.groupby("ticker_yahoo"):
            if not ticker:
                continue
            values = [str(value) for value in group["currency"] if str(value).strip()]
            if values:
                result[str(ticker)] = values[-1]
        return result

    def run(
        self,
        *,
        transactions_path: Path,
        market_data: pd.DataFrame,
        existing_histories: Mapping[str, pd.DataFrame],
        base_currency: str = "EUR",
        initial_cash: float = 0.0,
        auto_fund: bool = True,
        use_provider_dividends: bool = True,
        reinvest_dividends: bool = False,
        dividend_tax_pct: float = 0.0,
        extra_transaction_cost_bps: float = 0.0,
        benchmark_ticker: str | None = None,
    ) -> PortfolioSimulationBundle:
        transactions = self.read_transactions(transactions_path)
        if transactions.empty:
            raise ValueError("The transaction ledger is empty.")
        asset_types = {"buy", "sell", "split"}
        tickers = tuple(
            dict.fromkeys(
                transactions.loc[transactions["type"].isin(asset_types), "ticker_yahoo"].dropna().astype(str)
            )
        )
        if not tickers:
            raise ValueError("The transaction ledger contains no security transactions.")
        first_transaction = pd.Timestamp(transactions["date"].min()).normalize()
        histories = self._histories(tickers, existing_histories, first_transaction)
        prices: dict[str, pd.Series] = {}
        for ticker, history in histories.items():
            series = _price_series(history)
            if series is not None:
                trade_rows = transactions.loc[
                    (transactions["ticker_yahoo"] == ticker)
                    & transactions["type"].isin({"buy", "sell"})
                    & (transactions["price"] > 0)
                ]
                trade_prices = pd.Series(
                    trade_rows["price"].to_numpy(dtype=float),
                    index=pd.DatetimeIndex(trade_rows["date"]),
                    dtype=float,
                )
                series = pd.concat([series, trade_prices]).sort_index()
                series = series[~series.index.duplicated(keep="last")]
                prices[ticker] = series
        missing_prices = sorted(set(tickers).difference(prices))
        if missing_prices:
            raise ValueError("No price histories could be loaded for: " + ", ".join(missing_prices))
        start = first_transaction
        end = max(series.index.max() for series in prices.values())
        currencies = self._currency_map(transactions, market_data, base_currency)
        fx_rates: dict[str, pd.Series] = {}
        for currency in sorted(set(currencies.values()) | {base_currency}):
            history = self.fx_provider.history_to_base(currency, start, end, base_currency)
            if not history.empty:
                fx_rates[currency] = history
        dividends = {
            ticker: self.market_provider.get_dividends(ticker) for ticker in prices if use_provider_dividends
        }
        result = simulate_transaction_ledger(
            prices,
            transactions,
            currencies,
            fx_rates,
            dividends,
            initial_cash=initial_cash,
            base_currency=base_currency,
            auto_fund=auto_fund,
            use_provider_dividends=use_provider_dividends,
            reinvest_dividends=reinvest_dividends,
            dividend_tax_pct=dividend_tax_pct,
            extra_transaction_cost_bps=extra_transaction_cost_bps,
            start=start,
            end=end,
        )
        benchmark_result = None
        normalized_benchmark = str(benchmark_ticker or "").strip().upper()
        if normalized_benchmark:
            benchmark_history = self.market_provider.download_price_histories(
                (normalized_benchmark,), period="max"
            ).get(normalized_benchmark, pd.DataFrame())
            benchmark_prices = _price_series(benchmark_history)
            if benchmark_prices is not None:
                benchmark_prices = benchmark_prices.loc[
                    (benchmark_prices.index >= result.equity_curve.index.min())
                    & (benchmark_prices.index <= result.equity_curve.index.max())
                ]
                if not benchmark_prices.empty:
                    daily_flows = result.external_flows.copy()
                    trading_index = benchmark_prices.index
                    aligned_flows = pd.Series(0.0, index=trading_index)
                    for timestamp, amount in daily_flows[daily_flows != 0].items():
                        position = trading_index.searchsorted(timestamp)
                        if position < len(trading_index):
                            aligned_flows.iloc[position] += float(amount)
                    benchmark_result = simulate_benchmark_with_flows(
                        benchmark_prices,
                        aligned_flows,
                    )
        return PortfolioSimulationBundle(
            result=result,
            transactions=transactions,
            benchmark=benchmark_result,
            benchmark_ticker=normalized_benchmark or None,
            currencies=currencies,
        )
