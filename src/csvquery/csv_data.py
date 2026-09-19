from __future__ import annotations

from typing import Self, Iterator

from csvquery.config import PipelineConfig
from csvquery.io_handlers.writer import write_rows
from csvquery.operations.count import Count
from csvquery.operations.filter import Filter
from csvquery.operations.group_by import GroupBy
from csvquery.operations.limit import Limit
from csvquery.operations.operation import Operation
from csvquery.operations.select import Select
from csvquery.operations.sort import Sort
from csvquery.io_handlers.reader import read_rows

from csvquery.schema.files import retrieve_validate_files
from csvquery.schema.validation import validate_schema, validate_columns
from csvquery.schema.types import Row
from csvquery.util.timer import timed


class CSVData:
    @timed("schema validation")
    def __init__(self, path: str, config: PipelineConfig | None = None) -> None:
        self._config = PipelineConfig() if config is None else config
        self._files = retrieve_validate_files(path)
        self._schema = validate_schema(self._files, self._config)
        self._operations: list[Operation] = []

    def filter(self, expression: str) -> Self:
        self._operations.append(Filter(expression, self._schema))
        return self

    def select(self, *columns: str) -> Self:
        validate_columns(self._schema, columns, "select")
        self._operations.append(Select(*columns))
        return self

    def sort(self, *columns: str, descending: bool = False) -> Self:
        validate_columns(self._schema, columns, "sort")
        self._operations.append(Sort(*columns,  schema=self._schema, descending=descending))
        return self

    def limit(self, n: int) -> Self :
        self._operations.append(Limit(n))
        return self

    def count(self, column: str = "*") -> Self:
        if column != "*":
            validate_columns(self._schema, (column,), "count")

        self._operations.append(Count(column))
        return self

    def group_by(self, group_col: str, agg_col: str, agg_func: str = "sum") -> Self:
        validate_columns(self._schema, (group_col, agg_col), "group_by")

        self._operations.append(GroupBy(group_col, agg_col, agg_func, self._schema))
        return self

    @timed("query execution")
    def save(self, path: str) -> None:
        rows = self._execute()
        write_rows(path, rows, self._config)

    def _execute(self) -> Iterator[Row]:
        rows = read_rows(self._files, list(self._schema.keys()), self._config)
        for operation in self._operations:
            rows = operation.apply(rows)
        return rows

    def __iter__(self) -> Iterator[Row]:
        return self._execute()

    def __repr__(self) -> str:
        operations = ", ".join(type(op).__name__ for op in self._operations)
        return f"CSVData(files={len(self._files)}, operations=[{operations}])"

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._operations.clear()