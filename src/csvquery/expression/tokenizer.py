from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    COLUMN = "column"
    OPERATOR = "operator"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    AND = "and"
    OR = "or"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    END = "end"

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int

