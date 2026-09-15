import csv
from multiprocessing import Pool, cpu_count
from pathlib import Path

import pandas as pd

from csvquery.schema.inference import get_data_types
from csvquery.types import BOOLEANS, NULL_TYPES, ColumnType, get_cell_type

CHUNK_SIZE = 1_000_000


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
