from __future__ import annotations

from importlib.metadata import version


def get_version() -> str:
    return version("api")
