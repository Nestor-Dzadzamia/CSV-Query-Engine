from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.types import Row


class Sort(Operation):
    def __init__(self, *columns: str, descending: bool = False) -> None:
        self._columns = columns
        self._descending = descending

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        raise NotImplementedError
