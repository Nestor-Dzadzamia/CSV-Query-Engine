from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.types import Row


class Limit(Operation):
    def __init__(self, n: int) -> None:
        self._n = n

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        counter = 0
        for row in rows:
            if counter >= self._n:
                return
            counter += 1
            yield row