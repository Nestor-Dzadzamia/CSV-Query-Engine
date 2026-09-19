import csv
from pathlib import Path

from csvquery.config import PipelineConfig
from csvquery.schema.types import ColumnType, get_cell_type
from csvquery.util.errors import SourceError


def get_data_types(file: Path, config: PipelineConfig) -> dict[str, ColumnType]:
    with open(file, newline="", encoding=config.encoding) as csv_file:
        records = csv.reader(csv_file)
        header = next(records, None)
        if header is None:
            raise SourceError("CSV file is empty")

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
