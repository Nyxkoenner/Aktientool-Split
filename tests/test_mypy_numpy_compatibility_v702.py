from __future__ import annotations

import tomllib
from pathlib import Path


def test_mypy_skips_modern_numpy_stubs_for_python311_target() -> None:
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    mypy = config["tool"]["mypy"]

    assert mypy["python_version"] == "3.11"
    assert mypy["follow_imports_for_stubs"] is True

    overrides = mypy["overrides"]
    numpy_override = next(
        override for override in overrides if override.get("module") == ["numpy", "numpy.*"]
    )
    assert numpy_override["follow_imports"] == "skip"
