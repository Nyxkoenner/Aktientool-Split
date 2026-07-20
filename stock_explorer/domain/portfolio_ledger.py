from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Mapping

import numpy as np
import pandas as pd

SUPPORTED_TRANSACTION_TYPES = {
    "buy",
    "sell",
    "deposit",
    "withdrawal",
    "dividend",
    "fee",
    "split",
}

_TRANSACTION_ALIASES = {
    "buy": "buy",
    "kauf": "buy",
    "sell": "sell",
    "verkauf": "sell",
    "deposit": "deposit",
    "einzahlung": "deposit",
    "withdrawal": "withdrawal",
    "auszahlung": "withdrawal",
    "dividend": "dividend",
    "dividende": "dividend",
    "fee": "fee",
    "gebuehr": "fee",
    "gebühr": "fee",
    "split": "split",
    "aktiensplit": "split",
}


@dataclass(frozen=True)
class LedgerSimulationResult:
    equity_curve: pd.Series
    cash_curve: pd.Series
    external_flows: pd.Series
    positions: pd.DataFrame
    final_value: float
    final_cash: float
    net_contributions: float
    time_weighted_return_pct: float | None
    money_weighted_return_pct: float | None
    max_drawdown_pct: float
    dividends_received: float
    fees_paid: float
    taxes_paid: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BenchmarkSimulationResult:
    equity_curve: pd.Series
    final_value: float
    money_weighted_return_pct: float | None
    max_drawdown_pct: float


def normalize_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Normalize the user transaction ledger while keeping backward compatibility.

    Existing V5/V6 files with BUY/SELL rows remain valid. Cash events can use the
    optional ``cash_amount`` column. For deposit, withdrawal, dividend and fee rows,
    ``price`` is accepted as a backward-compatible amount field.
    """

    columns = [
        "date",
        "ticker_yahoo",
        "type",
        "shares",
        "price",
        "currency",
        "fees",
        "cash_amount",
        "comment",
    ]
    if transactions is None or transactions.empty:
        return pd.DataFrame(columns=columns)
    frame = transactions.copy()
    for column, default in {
        "ticker_yahoo": "",
        "shares": 0.0,
        "price": 0.0,
        "currency": "",
        "fees": 0.0,
        "cash_amount": np.nan,
        "comment": "",
    }.items():
        if column not in frame.columns:
            frame[column] = default
    required = {"date", "type"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing transaction columns: {', '.join(sorted(missing))}")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None)
    frame["type"] = frame["type"].astype(str).str.strip().str.lower().map(_TRANSACTION_ALIASES)
    frame["ticker_yahoo"] = frame["ticker_yahoo"].fillna("").astype(str).str.strip().str.upper()
    frame["currency"] = frame["currency"].fillna("").astype(str).str.strip()
    for column in ["shares", "price", "fees", "cash_amount"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["shares"] = frame["shares"].fillna(0.0)
    frame["price"] = frame["price"].fillna(0.0)
    frame["fees"] = frame["fees"].fillna(0.0)
    frame["comment"] = frame["comment"].fillna("").astype(str)
    frame = frame.dropna(subset=["date", "type"])
    frame = frame[frame["type"].isin(SUPPORTED_TRANSACTION_TYPES)].copy()
    cash_types = {"deposit", "withdrawal", "dividend", "fee"}
    fallback_amount = frame["price"].where(frame["type"].isin(cash_types), np.nan)
    frame["cash_amount"] = frame["cash_amount"].fillna(fallback_amount).fillna(0.0)
    return frame[columns].sort_values(["date", "ticker_yahoo", "type"]).reset_index(drop=True)


def _clean_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").dropna()
    values.index = pd.to_datetime(values.index, errors="coerce")
    values = values.loc[~values.index.isna()]
    if getattr(values.index, "tz", None) is not None:
        values.index = values.index.tz_localize(None)
    return values.sort_index()[~values.index.duplicated(keep="last")]


def _aligned_rate(
    rates: Mapping[str, pd.Series],
    currency: str,
    index: pd.DatetimeIndex,
    base_currency: str,
) -> pd.Series:
    code = str(currency or base_currency).strip()
    normalized = {"GBX": "GBP", "GBp": "GBP", "p": "GBP"}.get(code, code.upper())
    multiplier = 0.01 if code in {"GBX", "GBp", "p"} else 1.0
    if normalized == base_currency.upper():
        return pd.Series(multiplier, index=index, dtype=float)
    raw = rates.get(code)
    if raw is None:
        raw = rates.get(normalized)
    if raw is None or raw.empty:
        return pd.Series(np.nan, index=index, dtype=float)
    clean = _clean_series(raw).reindex(index).ffill().bfill()
    return clean.astype(float)


def _rate_on(
    rates: Mapping[str, pd.Series],
    currency: str,
    timestamp: pd.Timestamp,
    base_currency: str,
) -> float | None:
    aligned = _aligned_rate(rates, currency, pd.DatetimeIndex([timestamp]), base_currency)
    value = aligned.iloc[0]
    return float(value) if pd.notna(value) else None


def _price_frame(prices: Mapping[str, pd.Series], index: pd.DatetimeIndex) -> pd.DataFrame:
    prepared: dict[str, pd.Series] = {}
    for ticker, series in prices.items():
        clean = _clean_series(series)
        if not clean.empty:
            prepared[str(ticker).upper()] = clean.reindex(index).ffill()
    if not prepared:
        return pd.DataFrame(index=index)
    return pd.DataFrame(prepared, index=index)


def _xnpv(rate: float, flows: list[tuple[pd.Timestamp, float]]) -> float:
    origin = flows[0][0]
    return sum(amount / ((1.0 + rate) ** ((timestamp - origin).days / 365.25)) for timestamp, amount in flows)


def money_weighted_return(
    cash_flows: pd.Series,
    final_value: float,
    final_date: date | datetime | pd.Timestamp | None = None,
) -> float | None:
    flows = _clean_series(cash_flows)
    if flows.empty or final_value < 0:
        return None
    points = [(pd.Timestamp(timestamp), -float(amount)) for timestamp, amount in flows.items()]
    valuation_date = pd.Timestamp(final_date if final_date is not None else flows.index[-1])
    valuation_date = valuation_date.tz_localize(None)
    points.append((valuation_date, float(final_value)))
    if not any(amount < 0 for _, amount in points) or not any(amount > 0 for _, amount in points):
        return None
    lower, upper = -0.9999, 1000.0
    low_value = _xnpv(lower, points)
    high_value = _xnpv(upper, points)
    if np.sign(low_value) == np.sign(high_value):
        return None
    for _ in range(200):
        middle = (lower + upper) / 2.0
        value = _xnpv(middle, points)
        if abs(value) < 1e-8:
            return middle * 100.0
        if np.sign(value) == np.sign(low_value):
            lower, low_value = middle, value
        else:
            upper = middle
    return ((lower + upper) / 2.0) * 100.0


def time_weighted_return(equity_curve: pd.Series, external_flows: pd.Series) -> float | None:
    equity = _clean_series(equity_curve)
    if len(equity) < 2:
        return None
    flows = _clean_series(external_flows).reindex(equity.index).fillna(0.0)
    previous = equity.shift(1)
    period_returns = (equity - flows) / previous - 1.0
    period_returns = period_returns.replace([np.inf, -np.inf], np.nan).dropna()
    if period_returns.empty:
        return None
    return float(((1.0 + period_returns).prod() - 1.0) * 100.0)


def _max_drawdown(curve: pd.Series) -> float:
    clean = _clean_series(curve)
    if clean.empty:
        return 0.0
    drawdown = clean / clean.cummax() - 1.0
    return float(drawdown.min() * 100.0)


def simulate_transaction_ledger(
    prices: Mapping[str, pd.Series],
    transactions: pd.DataFrame,
    currencies: Mapping[str, str],
    fx_rates: Mapping[str, pd.Series] | None = None,
    dividend_frames: Mapping[str, pd.DataFrame] | None = None,
    *,
    initial_cash: float = 0.0,
    base_currency: str = "EUR",
    auto_fund: bool = True,
    use_provider_dividends: bool = True,
    reinvest_dividends: bool = False,
    dividend_tax_pct: float = 0.0,
    extra_transaction_cost_bps: float = 0.0,
    start: date | datetime | pd.Timestamp | None = None,
    end: date | datetime | pd.Timestamp | None = None,
) -> LedgerSimulationResult:
    frame = normalize_transactions(transactions)
    price_dates = [timestamp for series in prices.values() for timestamp in _clean_series(series).index]
    transaction_dates = list(frame["date"]) if not frame.empty else []
    all_dates = price_dates + transaction_dates
    if not all_dates:
        raise ValueError("No dates available for the portfolio simulation.")
    start_ts = pd.Timestamp(start if start is not None else min(all_dates)).tz_localize(None).normalize()
    end_ts = pd.Timestamp(end if end is not None else max(all_dates)).tz_localize(None).normalize()
    if end_ts < start_ts:
        raise ValueError("The simulation end date must not be before the start date.")
    index = pd.date_range(start_ts, end_ts, freq="D")
    price_table = _price_frame(prices, index)
    if price_table.empty:
        raise ValueError("No usable price histories are available.")
    fx_map = fx_rates or {}
    tax_rate = min(max(float(dividend_tax_pct), 0.0), 100.0) / 100.0
    cost_rate = max(float(extra_transaction_cost_bps), 0.0) / 10_000.0

    positions = {ticker: 0.0 for ticker in price_table.columns}
    cash = float(initial_cash)
    external = pd.Series(0.0, index=index, dtype=float)
    if initial_cash:
        external.iloc[0] += float(initial_cash)
    equity_values: list[float] = []
    cash_values: list[float] = []
    warnings: list[str] = []
    dividends_received = 0.0
    fees_paid = 0.0
    taxes_paid = 0.0

    grouped_transactions = {
        timestamp: group for timestamp, group in frame.groupby(frame["date"].dt.normalize())
    }
    dividend_events: dict[pd.Timestamp, list[tuple[str, float]]] = {}
    explicit_dividend_keys = {
        (pd.Timestamp(row["date"]).normalize(), str(row["ticker_yahoo"]).upper())
        for _, row in frame.loc[frame["type"] == "dividend"].iterrows()
    }
    if use_provider_dividends:
        for ticker, dividends in (dividend_frames or {}).items():
            if dividends is None or dividends.empty:
                continue
            local = dividends.copy()
            if "date" not in local.columns or "amount" not in local.columns:
                continue
            local["date"] = pd.to_datetime(local["date"], errors="coerce").dt.tz_localize(None).dt.normalize()
            local["amount"] = pd.to_numeric(local["amount"], errors="coerce")
            for _, row in local.dropna(subset=["date", "amount"]).iterrows():
                timestamp = pd.Timestamp(row["date"])
                normalized_ticker = str(ticker).upper()
                has_explicit = (timestamp, normalized_ticker) in explicit_dividend_keys or (
                    timestamp,
                    "",
                ) in explicit_dividend_keys
                if start_ts <= timestamp <= end_ts and not has_explicit:
                    dividend_events.setdefault(timestamp, []).append(
                        (normalized_ticker, float(row["amount"]))
                    )

    for timestamp in index:
        day_transactions = grouped_transactions.get(timestamp)
        if day_transactions is not None:
            for _, transaction in day_transactions.iterrows():
                event_type = str(transaction["type"])
                ticker = str(transaction["ticker_yahoo"]).upper()
                currency = str(transaction["currency"] or currencies.get(ticker, base_currency))
                fx = _rate_on(fx_map, currency, timestamp, base_currency)
                if fx is None:
                    warnings.append(f"Missing FX rate for {currency} on {timestamp.date()}.")
                    continue
                shares = float(transaction["shares"] or 0.0)
                price = float(transaction["price"] or 0.0)
                explicit_fees = max(float(transaction["fees"] or 0.0), 0.0) * fx
                amount = max(float(transaction["cash_amount"] or 0.0), 0.0) * fx
                if event_type == "deposit":
                    cash += amount
                    external.loc[timestamp] += amount
                elif event_type == "withdrawal":
                    cash -= amount
                    external.loc[timestamp] -= amount
                elif event_type == "buy" and ticker:
                    trade_value = shares * price * fx
                    variable_fee = trade_value * cost_rate
                    total_outflow = trade_value + explicit_fees + variable_fee
                    if cash + 1e-9 < total_outflow and auto_fund:
                        funding = total_outflow - cash
                        cash += funding
                        external.loc[timestamp] += funding
                    elif cash + 1e-9 < total_outflow:
                        warnings.append(f"Negative cash after purchase of {ticker} on {timestamp.date()}.")
                    cash -= total_outflow
                    positions[ticker] = positions.get(ticker, 0.0) + shares
                    fees_paid += explicit_fees + variable_fee
                elif event_type == "sell" and ticker:
                    available = positions.get(ticker, 0.0)
                    sold = min(shares, available)
                    if shares > available + 1e-9:
                        warnings.append(f"Sale quantity exceeds {ticker} holdings on {timestamp.date()}.")
                    trade_value = sold * price * fx
                    variable_fee = trade_value * cost_rate
                    cash += trade_value - explicit_fees - variable_fee
                    positions[ticker] = max(available - sold, 0.0)
                    fees_paid += explicit_fees + variable_fee
                elif event_type == "dividend":
                    tax = amount * tax_rate
                    cash += amount - tax
                    dividends_received += amount
                    taxes_paid += tax
                elif event_type == "fee":
                    cash -= amount
                    fees_paid += amount
                elif event_type == "split" and ticker:
                    ratio = shares if shares > 0 else price
                    if ratio > 0:
                        positions[ticker] = positions.get(ticker, 0.0) * ratio
                    else:
                        warnings.append(f"Invalid split ratio for {ticker} on {timestamp.date()}.")

        for ticker, amount_per_share in dividend_events.get(timestamp, []):
            held = positions.get(ticker, 0.0)
            if held <= 0:
                continue
            currency = currencies.get(ticker, base_currency)
            fx = _rate_on(fx_map, currency, timestamp, base_currency)
            if fx is None:
                warnings.append(f"Missing dividend FX rate for {ticker} on {timestamp.date()}.")
                continue
            gross = held * amount_per_share * fx
            tax = gross * tax_rate
            net = gross - tax
            dividends_received += gross
            taxes_paid += tax
            if reinvest_dividends:
                price_value = price_table.at[timestamp, ticker] if ticker in price_table.columns else np.nan
                if pd.notna(price_value) and price_value > 0:
                    local_price_base = float(price_value) * fx
                    positions[ticker] = held + net / local_price_base
                else:
                    cash += net
            else:
                cash += net

        market_value = 0.0
        for ticker, shares_held in positions.items():
            if shares_held == 0 or ticker not in price_table.columns:
                continue
            price_value = price_table.at[timestamp, ticker]
            if pd.isna(price_value):
                continue
            currency = currencies.get(ticker, base_currency)
            fx = _rate_on(fx_map, currency, timestamp, base_currency)
            if fx is None:
                continue
            market_value += shares_held * float(price_value) * fx
        cash_values.append(cash)
        equity_values.append(cash + market_value)

    equity_curve = pd.Series(equity_values, index=index, name="portfolio_value")
    cash_curve = pd.Series(cash_values, index=index, name="cash")
    position_rows = [
        {"ticker_yahoo": ticker, "shares": shares}
        for ticker, shares in positions.items()
        if abs(shares) > 1e-12
    ]
    net_contributions = float(external.sum())
    return LedgerSimulationResult(
        equity_curve=equity_curve,
        cash_curve=cash_curve,
        external_flows=external,
        positions=pd.DataFrame(position_rows),
        final_value=float(equity_curve.iloc[-1]),
        final_cash=float(cash_curve.iloc[-1]),
        net_contributions=net_contributions,
        time_weighted_return_pct=time_weighted_return(equity_curve, external),
        money_weighted_return_pct=money_weighted_return(
            external,
            float(equity_curve.iloc[-1]),
            equity_curve.index[-1],
        ),
        max_drawdown_pct=_max_drawdown(equity_curve),
        dividends_received=float(dividends_received),
        fees_paid=float(fees_paid),
        taxes_paid=float(taxes_paid),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def simulate_benchmark_with_flows(
    price_series: pd.Series,
    external_flows: pd.Series,
    *,
    initial_value: float = 0.0,
) -> BenchmarkSimulationResult:
    prices = _clean_series(price_series)
    if prices.empty:
        raise ValueError("No benchmark history available.")
    index = prices.index
    flows = _clean_series(external_flows).reindex(index).fillna(0.0)
    units = 0.0
    cash = float(initial_value)
    values: list[float] = []
    for timestamp, price in prices.items():
        flow = float(flows.loc[timestamp])
        if flow > 0:
            units += flow / float(price)
        elif flow < 0:
            units -= min(units, abs(flow) / float(price))
        values.append(cash + units * float(price))
    curve = pd.Series(values, index=index, name="benchmark")
    return BenchmarkSimulationResult(
        equity_curve=curve,
        final_value=float(curve.iloc[-1]),
        money_weighted_return_pct=money_weighted_return(
            flows,
            float(curve.iloc[-1]),
            curve.index[-1],
        ),
        max_drawdown_pct=_max_drawdown(curve),
    )
