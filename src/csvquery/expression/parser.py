from __future__ import annotations

from dataclasses import dataclass

from csvquery.expression.tokenizer import Token, TokenType, tokenize
from csvquery.util.errors import ExpressionError


@dataclass(frozen=True)
class Comparison:
    column: str
    operator: str
    value: str
    value_type: TokenType


@dataclass(frozen=True)
class And:
    left: Node
    right: Node


@dataclass(frozen=True)
class Or:
    left: Node
    right: Node


Node = Comparison | And | Or


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._position = 0

    def parse(self) -> Node:
        node = self._or_expr()
        if self._peek().type is not TokenType.END:
            raise ExpressionError(f"unexpected {self._peek().value!r} at position {self._peek().position}")
        return node

    def _or_expr(self) -> Node:
        node = self._and_expr()
        while self._peek().type is TokenType.OR:
            self._advance()
            node = Or(node, self._and_expr())
        return node

    def _and_expr(self) -> Node:
        node = self._primary()
        while self._peek().type is TokenType.AND:
            self._advance()
            node = And(node, self._primary())
        return node

    def _primary(self) -> Node:
        if self._peek().type is TokenType.LEFT_PAREN:
            self._advance()
            node = self._or_expr()
            self._expect(TokenType.RIGHT_PAREN)
            return node
        return self._comparison()

    def _comparison(self) -> Comparison:
        column = self._expect(TokenType.COLUMN)
        operator = self._expect(TokenType.OPERATOR)
        value = self._advance()
        if value.type not in (TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN):
            raise ExpressionError(f"expected a value after {operator.value!r} at position {value.position}")
        return Comparison(column.value, operator.value, value.value, value.type)

    def _peek(self) -> Token:
        return self._tokens[self._position]

    def _advance(self) -> Token:
        token = self._tokens[self._position]
        self._position += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._advance()
        if token.type is not token_type:
            raise ExpressionError(f"expected {token_type.value} but got {token.value!r} at position {token.position}")
        return token


def parse(expression: str) -> Node:
    return Parser(tokenize(expression)).parse()