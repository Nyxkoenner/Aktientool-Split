from stock_explorer import __version__
from stock_explorer.config import APP_VERSION


def test_package_and_display_versions_match() -> None:
    assert APP_VERSION == __version__ == "7.2.2"
