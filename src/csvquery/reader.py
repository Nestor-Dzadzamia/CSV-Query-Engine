from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from csvquery.types import Row


def read_rows(files: list[Path], header: list[str]) -> Iterator[Row]:
    for file_path in files:
        with file_path.open(newline="", encoding="utf-8-sig") as csv_file:
            records = csv.reader(csv_file) # generatoria esec
            next(records, None) # header ar mchirdeba

            for record in records:
                yield dict(zip(header, record))