from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.types import Row


class Filter(Operation):
    def __init__(self, expression: str) -> None:
        self._expression = expression

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        raise NotImplementedError
