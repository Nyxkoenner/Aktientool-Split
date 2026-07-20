from __future__ import annotations

import pandas as pd
import pytest

from stock_explorer.domain.portfolio_ledger import (
    money_weighted_return,
    normalize_transactions,
    simulate_transaction_ledger,
)


def test_normalize_transactions_supports_cash_events_and_german_aliases() -> None:
    frame = pd.DataFrame(
        [
            {
                "date": "2025-01-01",
                "ticker_yahoo": "alv.de",
                "type": "Kauf",
                "shares": 2,
                "price": 100,
            },
            {
                "date": "2026-01-02",
                "type": "Einzahlung",
                "price": 500,
                "currency": "EUR",
            },
        ]
    )
    normalized = normalize_transactions(frame)
    assert normalized.loc[0, "ticker_yahoo"] == "ALV.DE"
    assert normalized.loc[0, "type"] == "buy"
    assert normalized.loc[1, "type"] == "deposit"
    assert normalized.loc[1, "cash_amount"] == pytest.approx(500.0)


def test_transaction_ledger_uses_actual_dividend_dates_and_costs() -> None:
    index = pd.DatetimeIndex(["2025-01-01", "2025-06-01", "2026-01-01"])
    transactions = pd.DataFrame(
        [
            {
                "date": "2025-01-01",
                "type": "DEPOSIT",
                "cash_amount": 100,
                "currency": "EUR",
            },
            {
                "date": "2025-01-01",
                "ticker_yahoo": "AAA",
                "type": "BUY",
                "shares": 5,
                "price": 10,
                "currency": "EUR",
                "fees": 1,
            },
        ]
    )
    dividends = {"AAA": pd.DataFrame({"date": [pd.Timestamp("2025-06-01")], "amount": [1.0]})}
    result = simulate_transaction_ledger(
        {"AAA": pd.Series([10.0, 11.0, 12.0], index=index)},
        transactions,
        {"AAA": "EUR"},
        dividend_frames=dividends,
        auto_fund=False,
        dividend_tax_pct=20.0,
    )
    assert result.final_value == pytest.approx(113.0)
    assert result.final_cash == pytest.approx(53.0)
    assert result.dividends_received == pytest.approx(5.0)
    assert result.taxes_paid == pytest.approx(1.0)
    assert result.fees_paid == pytest.approx(1.0)
    assert result.net_contributions == pytest.approx(100.0)
    assert result.time_weighted_return_pct is not None
    assert result.money_weighted_return_pct is not None


def test_explicit_dividend_prevents_provider_double_counting() -> None:
    index = pd.date_range("2026-01-01", periods=3, freq="D")
    transactions = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "type": "DEPOSIT",
                "cash_amount": 100,
                "currency": "EUR",
            },
            {
                "date": "2026-01-01",
                "ticker_yahoo": "AAA",
                "type": "BUY",
                "shares": 5,
                "price": 10,
                "currency": "EUR",
            },
            {
                "date": "2026-01-02",
                "ticker_yahoo": "AAA",
                "type": "DIVIDEND",
                "cash_amount": 5,
                "currency": "EUR",
            },
        ]
    )
    dividends = {"AAA": pd.DataFrame({"date": [pd.Timestamp("2026-01-02")], "amount": [1.0]})}
    result = simulate_transaction_ledger(
        {"AAA": pd.Series([10.0, 10.0, 10.0], index=index)},
        transactions,
        {"AAA": "EUR"},
        dividend_frames=dividends,
        auto_fund=False,
    )
    assert result.dividends_received == pytest.approx(5.0)
    assert result.final_value == pytest.approx(105.0)


def test_money_weighted_return_uses_final_valuation_date() -> None:
    flows = pd.Series([100.0], index=[pd.Timestamp("2025-01-01")])
    result = money_weighted_return(flows, 110.0, pd.Timestamp("2026-01-01"))
    assert result == pytest.approx(10.0, abs=0.05)
