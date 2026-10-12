from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from csvquery.schema.types import Row


class Operation(ABC):
    @abstractmethod
    def apply(self, rows: Iterator[Row]) -> Iterator[Row]: ...
