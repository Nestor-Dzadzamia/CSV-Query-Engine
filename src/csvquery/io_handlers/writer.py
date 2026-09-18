import csv
from typing import Iterable
from operator import itemgetter

from csvquery.config import PipelineConfig
from csvquery.schema.types import Row


def write_rows(path: str, rows: Iterable[Row], config: PipelineConfig) -> None:
    row_iterator = iter(rows)
    first_row = next(row_iterator, None)

    if first_row is None:
        return

    headers = list(first_row.keys())

    if len(headers) == 1:
        getter = lambda r: (r[headers[0]],)
    else:
        getter = itemgetter(*headers)


    with open(path, mode="w", newline="", encoding=config.encoding, buffering=8 * 1024 * 1024) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(headers)
        writer.writerow(getter(first_row))
        writer.writerows(map(getter, row_iterator))