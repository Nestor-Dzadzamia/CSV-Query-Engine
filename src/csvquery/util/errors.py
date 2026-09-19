

class CSVQueryError(Exception):
    ...


class SourceError(CSVQueryError):
    ...


class SchemaError(CSVQueryError):
    ...


class ColumnError(CSVQueryError):
    ...


class ExpressionError(CSVQueryError):
    ...


class OperationError(CSVQueryError):
    ...