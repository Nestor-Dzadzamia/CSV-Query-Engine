from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.operations.types import cast
from csvquery.schema.types import Row, ColumnType


class Sort(Operation):
    def __init__(self, *columns: str, schema: dict[str, ColumnType], descending: bool = False) -> None:
        self._columns = columns
        self._descending = descending
        self._schema = schema

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        # (check)
        all_rows = list(rows)
        all_rows.sort(key=self._key, reverse=self._descending)

        for row in all_rows:
            yield row

    def _key(self, row: Row):
        key = []
        for column in self._columns:
            value = cast(row[column], self._schema[column])
            key.append((value is None, value))
        return tuple(key)
