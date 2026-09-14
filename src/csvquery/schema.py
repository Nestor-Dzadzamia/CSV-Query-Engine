import csv
from enum import Enum
from pathlib import Path
from multiprocessing import Pool, cpu_count

NULL_TYPES = {"", "NA", "N/A", "NULL", "null"}
NOT_NUMBERS = {"inf", "-inf", "+inf", "infinity", "-infinity", "+infinity", "nan", "-nan", "+nan"}

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

    if cell.lower() not in NOT_NUMBERS:
        try:
            float(cell)
            return ColumnType.FLOAT
        except ValueError:
            pass
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

        width = len(expected_data_types)
        checks = [
            (index, column, expected_data_type)
            for index, (column, expected_data_type) in enumerate(expected_data_types.items())
            if expected_data_type is not ColumnType.STRING
        ]

        for row_number, record in enumerate(records, start=1):  # romeli line ar varga gasagebad
            if len(record) != width:  # cell ebis raodenoba unda emtxveodes columnebis raodenobas
                raise ValueError(f"Expected {len(expected_data_types.keys())} cells, got {len(record)}")

            for index,  column_name, expected_data_type in checks:
                raw_cell = record[index]
                data_type_of_raw_cell = get_cell_type(raw_cell)

                if data_type_of_raw_cell is None:
                    continue

                if data_type_of_raw_cell != expected_data_type:
                    raise ValueError(
                        f"{file} row {row_number}, column {column_name}: expected {expected_data_type.value} but got {data_type_of_raw_cell.value}"
                    )


def validate_schema(files: list[Path]) -> dict[str, ColumnType]:
    expected_data_types = get_data_types(files[0])

    process_args = [(file, expected_data_types) for file in files]

    with Pool(processes=min(cpu_count(), len(files))) as pool:
        pool.starmap(validate_file_schema, process_args)

    return expected_data_types


def retrieve_validate_files(path: str) -> list[Path]:
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