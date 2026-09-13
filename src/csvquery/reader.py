from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from csvquery.types import Row


def read_rows(files: list[Path], header: list[str]) -> Iterator[Row]:
    width = len(header)

    for file_path in files:
        with file_path.open(newline="", encoding="utf-8-sig") as csv_file:
            records = csv.reader(csv_file)
            next(records, None)

            for record in records:
                if record == [""]:
                    continue
                if len(record) < width:
                    record = record + [""] * (width - len(record))
                elif len(record) > width:
                    record = record[:width]
                yield dict(zip(header, record))
