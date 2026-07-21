"""Zusätzlicher Regressionstest für die zentrale Anwendungsversion."""

import re

from stock_explorer import __version__
from stock_explorer.config import APP_VERSION

SEMANTIC_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def test_visible_and_package_version_match() -> None:
    """Künftige Patch-Releases dürfen keinen alten Versionswert erwarten."""
    assert APP_VERSION == __version__
    assert SEMANTIC_VERSION_PATTERN.fullmatch(APP_VERSION)
