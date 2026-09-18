import pytest
from csvquery.expression.compiler import compile_expression
from csvquery.expression.parser import parse
from csvquery.schema.types import ColumnType

SCHEMA = {"price": ColumnType.FLOAT, "brand": ColumnType.STRING, "qty": ColumnType.INTEGER}


def condition(expression):
    return compile_expression(parse(expression), SCHEMA)


def test_numeric():
    c = condition("price > 100")
    assert c({"price": "150.0"}) and not c({"price": "50.0"})


def test_string():
    c = condition("brand == 'apple'")
    assert c({"brand": "apple"}) and not c({"brand": "samsung"})


def test_and():
    c = condition("price > 100 AND brand == 'apple'")
    assert c({"price": "150", "brand": "apple"})
    assert not c({"price": "150", "brand": "samsung"})


def test_or():
    c = condition("price > 1000 OR brand == 'apple'")
    assert c({"price": "5", "brand": "apple"})


def test_precedence():
    c = condition("brand == 'x' OR price > 100 AND qty > 5")
    assert c({"brand": "x", "price": "0", "qty": "0"})
    assert not c({"brand": "y", "price": "200", "qty": "1"})


def test_null_never_matches():
    c = condition("price > 0")
    assert not c({"price": ""})


def test_unknown_column():
    with pytest.raises(ValueError, match="invalid column"):
        condition("nope > 1")


def test_type_mismatch():
    with pytest.raises(ValueError, match="can't compare"):
        condition("price > 'abc'")