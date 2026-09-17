from __future__ import annotations
from typing import Self, Iterator

from csvquery.io_handlers.writer import write_rows
from csvquery.operations.filter import Filter
from csvquery.operations.limit import Limit
from csvquery.operations.operation import Operation
from csvquery.operations.select import Select
from csvquery.operations.sort import Sort
from csvquery.io_handlers.reader import read_rows

from csvquery.schema.files import retrieve_validate_files
from csvquery.schema.validation import validate_schema
from csvquery.schema.types import Row

class CSVData:
    def __init__(self, path: str) -> None:
        self._files = retrieve_validate_files(path)
        self._schema = validate_schema(self._files)
        self._operations: list[Operation] = []

    def filter(self, expression: str) -> Self:
        # validate_expression(expression)
        self._operations.append(Filter(expression, self._schema))
        return self

    def select(self, *columns: str) -> Self:
        self._validate_columns(columns, "select")
        self._operations.append(Select(*columns))
        return self

    def sort(self, *columns: str, descending: bool = False) -> Self:
        self._validate_columns(columns, "sort")
        self._operations.append(Sort(*columns,  schema=self._schema, descending=descending))
        return self

    def limit(self, n: int) -> Self:
        self._operations.append(Limit(n))
        return self

    def save(self, path: str) -> None:
        rows = self._execute()
        write_rows(path, rows)

    def _execute(self) -> Iterator[Row]:
        rows = read_rows(self._files, list(self._schema.keys()))
        for operation in self._operations:
            rows = operation.apply(rows)
        return rows

    def __iter__(self) -> Iterator[Row]:
        return self._execute()

    def _validate_columns(self, columns: tuple[str, ...], operation: str) -> None:
        for column in columns:
            if column not in self._schema:
                raise ValueError(f"Invalid column '{column}' on operation '{operation}'")