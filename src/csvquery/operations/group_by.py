from __future__ import annotations

from collections.abc import Iterator

from csvquery.operations.operation import Operation
from csvquery.operations.types import cast
from csvquery.schema.types import NULL_TYPES, ColumnType, Row
from csvquery.util.errors import OperationError

AGGREGATIONS = ("sum", "count", "avg", "min", "max")


class GroupBy(Operation):
    def __init__(self, group_col: str, agg_col: str, agg_func: str, schema: dict[str, ColumnType]) -> None:
        agg_func = agg_func.lower()
        if agg_func not in AGGREGATIONS:
            raise OperationError(f"invalid aggregation '{agg_func}', expected one of {AGGREGATIONS}")
        if agg_func != "count" and schema[agg_col] not in (ColumnType.INTEGER, ColumnType.FLOAT):
            raise OperationError(f"can't {agg_func} column '{agg_col}' of type {schema[agg_col].value}")

        self.group_col = group_col
        self.agg_col = agg_col
        self.agg_func = agg_func
        self._agg_type = schema[agg_col]

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        totals: dict[str, float] = {}
        counts: dict[str, int] = {}

        for row in rows:
            group = row[self.group_col]
            raw = row[self.agg_col]

            if group not in counts:
                counts[group] = 0
                totals[group] = 0.0

            if raw in NULL_TYPES:
                continue

            counts[group] += 1
            if self.agg_func == "count":
                continue

            value = cast(raw, self._agg_type)
            assert isinstance(value, (int, float))

            if self.agg_func in ("sum", "avg"):
                totals[group] += value
            elif self.agg_func == "min":
                totals[group] = value if counts[group] == 1 else min(totals[group], value)
            elif self.agg_func == "max":
                totals[group] = value if counts[group] == 1 else max(totals[group], value)

        result_name = f"{self.agg_func.upper()}({self.agg_col})"
        for group in counts:
            if self.agg_func == "count":
                result: int | float = counts[group]
            elif self.agg_func == "avg":
                result = totals[group] / counts[group] if counts[group] else 0.0
            else:
                result = totals[group]
            yield {self.group_col: group, result_name: str(result)}