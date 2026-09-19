from dataclasses import dataclass
from enum import Enum
import re
from csvquery.util.errors import ExpressionError

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

KEYWORDS = {"AND": TokenType.AND, "OR": TokenType.OR}

TOKEN_PATTERN = re.compile(
    r"""
    (?P<space>\s+)
  | (?P<operator>>=|<=|==|!=|>|<)
  | (?P<left_paren>\()
  | (?P<right_paren>\))
  | (?P<number>-?\d+(?:\.\d+)?)
  | (?P<string>'[^']*'|"[^"]*")
  | (?P<word>[A-Za-z_]\w*)
    """,
    re.VERBOSE,
)


def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0

    while position < len(expression):
        match = TOKEN_PATTERN.match(expression, position)
        if match is None:
            raise ExpressionError(f"unexpected character {expression[position]!r} at position {position}")

        kind = match.lastgroup
        text = match.group()

        if kind == "space":
            pass
        elif kind == "operator":
            tokens.append(Token(TokenType.OPERATOR, text, position))
        elif kind == "left_paren":
            tokens.append(Token(TokenType.LEFT_PAREN, text, position))
        elif kind == "right_paren":
            tokens.append(Token(TokenType.RIGHT_PAREN, text, position))
        elif kind == "number":
            tokens.append(Token(TokenType.NUMBER, text, position))
        elif kind == "string":
            tokens.append(Token(TokenType.STRING, text[1:-1], position))
        elif kind == "word":
            upper = text.upper()
            if upper in KEYWORDS:
                tokens.append(Token(KEYWORDS[upper], upper, position))
            elif upper in ("TRUE", "FALSE"):
                tokens.append(Token(TokenType.BOOLEAN, upper.lower(), position))
            else:
                tokens.append(Token(TokenType.COLUMN, text, position))

        position = match.end()

    tokens.append(Token(TokenType.END, "", position))
    return tokens