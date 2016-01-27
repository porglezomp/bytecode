import math

import hypothesis
from hypothesis import given, example
from hypothesis.strategies import text, floats, integers

import lexer
from lexer import Ident, Num


@given(text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'))
@example('if')
def test_identifiers(name):
    hypothesis.assume(name)
    hypothesis.assume(not name[0].isdigit())
    assert list(lexer.tokenize(name)) == [Ident(name)]


@given(floats(allow_infinity=False, allow_nan=False))
def test_floats(num):
    hypothesis.assume(not math.isinf(num))
    assert list(lexer.tokenize('{:.1024f}'.format(num))) == [Num(num)]


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
