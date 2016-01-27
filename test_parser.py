import lexer
import bcparser
from bcast import IfElse, Num, Return, BinOp


def test_basic_operators():
    ops = ['+', '-', '*', '/', '^', '<', '>', '<=', '>=', '==', '!=']
    for op in ops:
        tokens = lexer.tokenize('1 {} 1'.format(op))
        assert bcparser.parse(tokens) == [BinOp(Num(1), op, Num(1))]


def test_operators():
    cases = [
        ('1 + 1', [BinOp(Num(1), '+', Num(1))]),
    ]
    for string, ast in cases:
        tokens = lexer.tokenize(string)
        assert bcparser.parse(tokens) == ast


def test_if_else():
    cases = [
        ('if 1 {}', [IfElse(Num(1), [], None)]),
        ('if 1 { return 0; }', [IfElse(Num(1), [Return(Num(0))], None)]),
        ('if 1 {} else {}', [IfElse(Num(1), [], [])]),
        ('if 1 {} else if 0 {}',
         [IfElse(Num(1), [], [IfElse(Num(0), [], None)])]),
        ('if 1 {} else if 0 {} else {}',
         [IfElse(Num(1), [], [IfElse(Num(0), [], [])])]),
    ]
    for string, ast in cases:
        tokens = lexer.tokenize(string)
        assert bcparser.parse(tokens) == ast
