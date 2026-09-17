from __future__ import annotations

import operator
import re

from collections.abc import Iterator, Callable

from csvquery.operations.operation import Operation
from csvquery.operations.types import cast
from csvquery.schema.types import Row, ColumnType

OPERATORS: dict[str, Callable] = {
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    ">": operator.gt,
}

EXPRESSION = re.compile(r"^\s*(\w+)\s*(>=|<=|==|!=|>|<)\s*(.+?)\s*$")


class Filter(Operation):
    def __init__(self, expression: str, schema: dict[str, ColumnType]) -> None:
        match = EXPRESSION.match(expression)

        if match is None:
            raise ValueError(f"invalid filter '{expression}', create filter according to grammar - COLUMN OPERATOR VALUE")

        column, operator, value = match.groups()

        if column not in schema:
            raise ValueError(f"invalid column '{column}' on operation 'filter'")

        if value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        self._column = column
        self._type = schema[column]
        self._compare_operator = OPERATORS[operator]

        try:
            self._value = cast(value, self._type)
        except ValueError:
            raise ValueError(f"can't compare value '{value}' on operation 'filter', {self._type.value} type needed")

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        for row in rows:
            target_cell = cast(row[self._column], self._type)
            if target_cell is not None and self._compare_operator(target_cell, self._value):
                yield row
