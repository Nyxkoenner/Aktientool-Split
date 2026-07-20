from stock_explorer.providers.base import MarketDataProvider
from stock_explorer.providers.registry import get_market_provider


def test_yahoo_provider_contract():
    provider = get_market_provider("yahoo")
    assert isinstance(provider, MarketDataProvider)
    assert provider.name


def test_empty_history_request():
    provider = get_market_provider("yahoo")
    assert provider.download_price_histories(()) == {}
