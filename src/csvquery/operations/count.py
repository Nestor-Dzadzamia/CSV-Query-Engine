from typing import Iterator

from csvquery.operations.operation import Operation
from csvquery.schema.types import Row, NULL_TYPES


class Count(Operation):
    def __init__(self, column: str) -> None:
        self._column = column

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        count = 0

        if self._column == "*":
            for _ in rows:
                count += 1
        else:
            for row in rows:
                if row[self._column] not in NULL_TYPES:
                    count += 1

        yield {f"COUNT({self._column})": str(count)}
