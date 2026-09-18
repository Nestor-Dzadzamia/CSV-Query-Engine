from csvquery.expression.tokenizer import TokenType, tokenize


def types(expression):
    return [t.type for t in tokenize(expression)]


def test_simple_comparison():
    assert types("price > 100") == [TokenType.COLUMN, TokenType.OPERATOR, TokenType.NUMBER, TokenType.END]


def test_string_value_strips_quotes():
    tokens = tokenize("brand == 'apple'")
    assert tokens[2].type == TokenType.STRING
    assert tokens[2].value == "apple"


def test_keywords_case_insensitive():
    assert types("a > 1 and b < 2") == types("a > 1 AND b < 2")


def test_two_char_operators():
    assert [t.value for t in tokenize("a >= 1")][1] == ">="


def test_parentheses():
    assert types("(a > 1)") == [TokenType.LEFT_PAREN, TokenType.COLUMN, TokenType.OPERATOR, TokenType.NUMBER, TokenType.RIGHT_PAREN, TokenType.END]


def test_negative_number():
    assert tokenize("a > -5")[2].value == "-5"


def test_bad_character():
    import pytest
    with pytest.raises(ValueError, match="position 4"):
        tokenize("a > $")