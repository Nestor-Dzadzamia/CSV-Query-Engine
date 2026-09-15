from __future__ import annotations
from typing import Self, Iterator
from csvquery.operations.filter import Filter
from csvquery.operations.limit import Limit
from csvquery.operations.operation import Operation
from csvquery.operations.select import Select
from csvquery.operations.sort import Sort
from csvquery.io_handlers.reader import read_rows

from csvquery.schema.files import retrieve_validate_files
from csvquery.schema.validation import validate_schema
from csvquery.types import Row

class CSVData:
    def __init__(self, path: str) -> None:
        self._open_path = path
        self._save_path = "default.csv"
        self._files = retrieve_validate_files(path)
        self._schema = validate_schema(self._files)
        self._operations: list[Operation] = []

    def filter(self, expression: str) -> Self:
        # validate_expression(expression)
        self._operations.append(Filter(expression))
        return self

    def select(self, *columns: str) -> Self:
        # validate_columns(columns)
        self._operations.append(Select(*columns))
        return self

    def sort(self, *columns: str, descending: bool = False) -> Self:
        # validate_columns(columns)
        self._operations.append(Sort(*columns, descending=descending))
        return self

    def limit(self, n: int) -> Self:
        self._operations.append(Limit(n))
        return self

    def save(self, path: str) -> None:
        self._save_path = path

    def _execute(self) -> Iterator[Row]:
        rows = read_rows(self._files, list(self._schema.keys()))
        for operation in self._operations:
            rows = operation.apply(rows)
        return rows

    def __iter__(self) -> Iterator[Row]:
        return self._execute()