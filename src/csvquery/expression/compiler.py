from __future__ import annotations

import operator
from collections.abc import Callable
from typing import Any

from csvquery.expression.parser import And, Comparison, Node
from csvquery.operations.types import cast
from csvquery.schema.types import ColumnType, Row

Condition = Callable[[Row], bool]

OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
}


def compile_expression(node: Node, schema: dict[str, ColumnType]) -> Condition:
    if isinstance(node, Comparison):
        return _compile_comparison(node, schema)

    left = compile_expression(node.left, schema)
    right = compile_expression(node.right, schema)

    if isinstance(node, And):
        return lambda row: left(row) and right(row)
    return lambda row: left(row) or right(row)


def _compile_comparison(node: Comparison, schema: dict[str, ColumnType]) -> Condition:
    if node.column not in schema:
        raise ValueError(f"invalid column '{node.column}' on operation 'filter'")

    column = node.column
    column_type = schema[column]
    compare = OPERATORS[node.operator]

    try:
        value = cast(node.value, column_type)
    except ValueError:
        raise ValueError(
            f"can't compare column '{column}' ({column_type.value}) with '{node.value}'"
        ) from None

    def condition(row: Row) -> bool:
        cell = cast(row[column], column_type)
        return cell is not None and compare(cell, value)

    return condition