import csv
import re
from enum import Enum
from pathlib import Path

NULL_TYPES = {"", "NA", "N/A", "NULL", "null"}


class ColumnType(Enum):
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"


def get_cell_type(raw_cell: str) -> ColumnType | None:
    cell = raw_cell.strip()
    if cell in NULL_TYPES:
        return None

    # satitaod cast (check)
    try:
        int(cell)
        return ColumnType.INTEGER
    except ValueError:
        ...

    try:
        if not re.match(r"[+-]?\s*\b(?:inf(?:inity)?|INF(?:INITY)?|Inf(?:inity)?)\b", cell, re.IGNORECASE) and cell != "nan": # es prosta -inf inf filtria, regex AIit davwere
            float(cell)
            return ColumnType.FLOAT
    except ValueError:
        ...
    return ColumnType.STRING


def get_data_types(file: Path) -> dict[str, ColumnType]:
    with open(file, newline="", encoding="utf-8-sig") as csv_file:
        records = csv.reader(csv_file)
        header = next(records, None)
        if header is None:
            raise ValueError("CSV file is empty")

        header = [column.strip() for column in header]
        types: dict[str, ColumnType | None] = {  # napovni type ebistvis
            column: None for column in header
        }
        unknown_columns = set(header)

        for record in records:
            for column, cell in zip(header, record):  # column : cell gadayola
                if column in unknown_columns:
                    cell_type = get_cell_type(cell)
                    if cell_type is not None:
                        types[column] = cell_type
                        unknown_columns.remove(column)

            if not unknown_columns:  # yvela svets aqvs type, anu unkown columns set carielia
                break

        # tu mteli sveti sul null ebia mashin defaultat String type
        return {column: cell_type or ColumnType.STRING for column, cell_type in types.items()}


def validate_file_schema(file: Path, expected_data_types: dict[str, ColumnType]) -> None:
    with open(file, newline="", encoding="utf-8-sig") as csv_file:
        records = csv.reader(csv_file)
        headers = next(records, None)

        if headers is None:
            raise ValueError(f"CSV file is empty {file}")

        headers = [column.strip() for column in headers]

        if len(headers) != len(expected_data_types.keys()):
            raise ValueError(f"Expected {len(expected_data_types)} columns, got {len(headers)}")

        for expected_column, actual_column in zip(expected_data_types.keys(), headers):
            if expected_column != actual_column:
                raise ValueError(
                    f"column mismatch, should be {expected_column}, got {actual_column} in {file}"
                )

        for row_number, record in enumerate(records, start=1): # romeli line ar varga gasagebad
            for column_name, expected_type, raw_cell in zip(expected_data_types.keys(), expected_data_types.values(), record):
                data_type_of_raw_cell = get_cell_type(raw_cell)

                if data_type_of_raw_cell is None:
                    continue

                if data_type_of_raw_cell != expected_type:
                    # print(record)
                    raise ValueError(
                        f" Error in {file} at row {row_number} on column {column_name} cell - {raw_cell}: expected {expected_type.value} but got {data_type_of_raw_cell.value}"
                    )


def validate_schema(files: list[Path]) -> dict[str, ColumnType]:
    expected_data_types = get_data_types(files[0])
    for file in files:
        validate_file_schema(file, expected_data_types)
    return expected_data_types


def retrieve_validate_files(path: str) -> list[Path]:
    """return the CSV files at `path`, which may be one file or a directory"""
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"The path {path!r} does not exist")

    if target.is_file():
        if target.suffix != ".csv":
            raise ValueError(f"not a CSV file: {path!r}")
        return [target]

    files = []

    for file in target.iterdir():
        if file.suffix != ".csv":
            continue
        files.append(file)

    files = sorted(files, key=lambda f: f.name) # aq vsortav, filesystemma sheileba aradeterministulad waikitxos

    if not files:
        raise ValueError(f"the directory {path!r} contains no .csv files")
    return files
