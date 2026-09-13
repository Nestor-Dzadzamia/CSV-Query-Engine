from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from csvquery.types import Row


class Operation(ABC):
    """One step in a query pipeline: takes a stream of rows, returns a stream of rows."""

    @abstractmethod
    def apply(self, rows: Iterator[Row]) -> Iterator[Row]:
        """Transform the incoming rows."""
