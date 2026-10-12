from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.schema.types import Row

class Select(Operation):
    def __init__(self, *columns: str) -> None:
        self._columns = columns

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        for row in rows:
            select = {
                column: row[column] for column in self._columns
            }
            yield Row(select)