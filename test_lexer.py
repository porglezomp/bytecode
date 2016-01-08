import lexer
from lexer import Ident, Num
from hypothesis import given
from hypothesis.strategies import text, floats, integers


@given(text())
def test_identifiers(name):
    assert list(lexer.tokenize(name)) == [Ident(name)]


@given(floats())
def test_floats(num):
    assert list(lexer.tokenize(str(num))) == [Num(num)]


@given(integers())
def test_ints(num):
    assert list(lexer.tokenize(str(num))) == [Num(num)]


def test_lexer():
    cases = [
        ("a", [Ident("a")]),
        ("b", [Ident("b")]),
        ("1", [Num(1)]),
    ]
    for inp, outp in cases:
        assert list(lexer.tokenize(inp)) == outp
