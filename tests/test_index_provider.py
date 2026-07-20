from __future__ import annotations

from pathlib import Path

from stock_explorer.providers.indexes import CompositeIndexProvider


def test_static_index_is_loaded_without_network(tmp_path: Path):
    provider = CompositeIndexProvider(
        local_paths={"Demo": tmp_path / "demo.csv"},
        static_constituents={
            "Demo": [
                {"name": "Alpha", "ticker_yahoo": "AAA.DE", "sector": "Industrials"},
                {"name": "Beta", "ticker_yahoo": "BBB.DE", "sector": "Technology"},
            ]
        },
        expected_counts={"Demo": 2},
        cache_dir=tmp_path / "cache",
        static_as_of="2026-07-20",
    )

    result = provider.load("Demo")

    assert len(result.frame) == 2
    assert result.frame["ticker_yahoo"].tolist() == ["AAA.DE", "BBB.DE"]
    assert "Offline" in result.source
