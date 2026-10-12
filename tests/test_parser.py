import pytest
from csvquery.util.errors import ExpressionError
from csvquery.expression.parser import And, Comparison, Or, parse
from csvquery.expression.tokenizer import TokenType


def test_single_comparison():
    assert parse("price > 100") == Comparison("price", ">", "100", TokenType.NUMBER)


def test_string_value():
    assert parse("brand == 'apple'") == Comparison("brand", "==", "apple", TokenType.STRING)


def test_and():
    tree = parse("a > 1 AND b < 2")
    assert isinstance(tree, And)
    assert tree.left.column == "a" and tree.right.column == "b"


def test_and_binds_tighter_than_or():
    tree = parse("a > 1 OR b > 2 AND c > 3")
    assert isinstance(tree, Or)
    assert isinstance(tree.left, Comparison)
    assert isinstance(tree.right, And)


def test_parentheses_override():
    tree = parse("(a > 1 OR b > 2) AND c > 3")
    assert isinstance(tree, And)
    assert isinstance(tree.left, Or)


def test_chained_and_is_left_associative():
    tree = parse("a > 1 AND b > 2 AND c > 3")
    assert isinstance(tree, And) and isinstance(tree.left, And)


def test_missing_value():
    with pytest.raises(ExpressionError, match="expected a value"):
        parse("price >")


def test_missing_close_paren():
    with pytest.raises(ExpressionError, match="expected"):
        parse("(a > 1")


def test_trailing_garbage():
    with pytest.raises(ExpressionError, match="unexpected"):
        parse("a > 1 b")