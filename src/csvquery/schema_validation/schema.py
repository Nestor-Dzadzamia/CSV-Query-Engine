import csv
from enum import Enum
from pathlib import Path
from multiprocessing import Pool, cpu_count
import pandas as pd

NULL_TYPES = {"", "NA", "N/A", "NULL", "null"}
NOT_NUMBERS = {"inf", "-inf", "+inf", "infinity", "-infinity", "+infinity", "nan", "-nan", "+nan"}
BOOLEANS = {"true", "false", "TRUE", "FALSE"}
CHUNK_SIZE = 1_000_000

class ColumnType(Enum):
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"


def get_cell_type(raw_cell: str) -> ColumnType | None:
    cell = raw_cell.strip()

    if cell in BOOLEANS:
        return ColumnType.BOOLEAN

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
        headers = next(csv.reader(csv_file), None)

    if headers is None:
        raise ValueError(f"CSV file is empty {file}")

    headers = [column.strip() for column in headers]
    if headers != list(expected_data_types):
        raise ValueError(f"{file}: columns {headers} do not match {list(expected_data_types)}")

    # mxolod numeric columnebis validurobas vcheqav, string svetshi tu ricxvia magalitad 101 ganvixilav rogorc strigns
    numeric_columns = [column for column, data_type in expected_data_types.items() if data_type in (ColumnType.INTEGER, ColumnType.FLOAT, ColumnType.INTEGER)]
    boolean_columns = [column for column, data_type in expected_data_types.items() if data_type is ColumnType.BOOLEAN]
    checked_columns = numeric_columns + boolean_columns
    if not checked_columns:
        return

    try:
        chunks = pd.read_csv( # aq chunk_size is morgeba sheileba yvelaze swafi ro iyos
            file,
            usecols=checked_columns,
            dtype={column: str for column in boolean_columns},
            chunksize=CHUNK_SIZE,
            na_values=list(NULL_TYPES),
            keep_default_na=False,
            encoding="utf-8-sig",
        ) # sia pandas chunk_size is xela data_frameebis
        for chunk in chunks:
            for column in numeric_columns:
                values = chunk[column].dropna() # am chunkis columnebis titoeuli svetis mnishvnelobebi
                expected_data_type = expected_data_types[column]

                if not pd.api.types.is_numeric_dtype(values):
                    for row, cell in values.items():
                        if get_cell_type(cell) is ColumnType.STRING:
                            raise ValueError(
                                f"{file} row {row + 1}: column {column} expected {expected_data_type.value} but got {cell}"
                            )

                if expected_data_type is ColumnType.INTEGER:
                    bad = values % 1 != 0 # anu integers velodebit da float weria
                    if bad.any(): # tu romelime value truea
                        row = bad.idxmax() # pirveli trues indexi
                        raise ValueError(
                            f"{file} row {row + 1}, column {column}: expected integer but got {values[row]}"
                        )
            for column in boolean_columns:
                values = chunk[column].dropna()
                bad = ~values.isin(BOOLEANS) # es ~ prosta flipavs anu not ivitaa
                if bad.any():
                    row = bad.idxmax()
                    raise ValueError(
                        f"{file} row {row + 1}, column {column}: expected boolean got {values[row]}"
                    )

    except pd.errors.ParserError as error:
        raise ValueError(f"{file}: {error}") from None

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