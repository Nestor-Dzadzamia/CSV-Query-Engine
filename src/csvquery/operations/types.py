from csvquery.schema.types import ColumnType, NULL_TYPES



def cast(cell: str, column_type: ColumnType) -> int | float | bool | str | None:
    if cell.strip() in NULL_TYPES:
        return None

    match column_type:
        case ColumnType.INTEGER: return int(cell)
        case ColumnType.FLOAT: return float(cell)
        case ColumnType.BOOLEAN: return cell.strip().lower() == "true"
        case ColumnType.STRING: return cell