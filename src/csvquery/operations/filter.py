from __future__ import annotations

from collections.abc import Iterator

from csvquery.expression.compiler import compile_expression
from csvquery.expression.parser import parse
from csvquery.operations.operation import Operation
from csvquery.schema.types import ColumnType, Row


class Filter(Operation):
    def __init__(self, expression: str, schema: dict[str, ColumnType]) -> None:
        self._condition = compile_expression(parse(expression), schema)

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        for row in rows:
            if self._condition(row):
                yield row