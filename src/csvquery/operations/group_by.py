from typing import Iterator
from csvquery.operations.operation import Operation
from csvquery.types import Row

class GroupBy(Operation):
    def __init__(self, group_col: str, agg_col: str, agg_func: str = "sum"):
        self.group_col = group_col
        self.agg_col = agg_col
        self.agg_func = agg_func.lower()

    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        aggregated_data: dict[str, float] = {}

        for row in rows:
            group_val = str(row.get(self.group_col, "Unknown"))
            try:
                numeric_val = float(row.get(self.agg_col, 0))
            except (ValueError, TypeError):
                continue

            if group_val not in aggregated_data:
                aggregated_data[group_val] = 0.0

            if self.agg_func == "sum":
                aggregated_data[group_val] += numeric_val
            elif self.agg_func == "count":
                aggregated_data[group_val] += 1

        for group_val, agg_val in aggregated_data.items():
            yield {self.group_col: group_val, self.agg_col: agg_val}