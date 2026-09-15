from enum import Enum

Row = dict[str, str]

NULL_TYPES = {"", "NA", "N/A", "NULL", "null"}
NOT_NUMBERS = {"inf", "-inf", "+inf", "infinity", "-infinity", "+infinity", "nan", "-nan", "+nan"}
BOOLEANS = {"true", "false", "TRUE", "FALSE"}


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
