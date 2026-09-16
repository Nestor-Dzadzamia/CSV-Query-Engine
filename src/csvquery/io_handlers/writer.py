from __future__ import annotations

from collections.abc import Iterable

from csvquery.types import Row
import csv


def write_rows(path: str, rows: Iterable[Row]) -> None:
    row_iterator = iter(rows)
    #pirveli row wamogeba nones shemtxvevashi defaultad ikos
    first_row = next(row_iterator, None)

    #carieli xoaraa data
    if first_row is None:
        return
    #svetebis saxelebi mogvaq
    headers = list(first_row.keys())
    #gavxsnat file
    with open(path, mode="w", newline="", encoding="utf-8") as csv_file:
        #sul ro tanmimdevrobit gaxsnas fielnames=headers
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        #pirveli row mogvaq
        writer.writeheader()
        #dictionarys matchavs keys headerebtan aorderebs
        writer.writerow(first_row)
        #dalshe 10gb wers automaturad
        writer.writerows(row_iterator)

