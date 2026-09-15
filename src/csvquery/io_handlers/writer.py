from __future__ import annotations

from collections.abc import Iterable

from csvquery.types import Row


def write_rows(path: str, rows: Iterable[Row]) -> None:
    raise NotImplementedError
