from __future__ import print_function
import re


class Lookahead:
    """
    Wrap a generator to include a single object of lookahead.
    Doesn't correctly handle generators which yield `None`.
    """
    def __init__(self, gen):
        self.gen = gen
        try:
            self._peek = self.gen.next()
        except StopIteration:
            self._peek = None

    def peek(self):
        return self._peek

    def __iter__(self):
        return self

    def next(self):
        value = self._peek
        if value is None:
            raise StopIteration

        try:
            self._peek = self.gen.next()
        except StopIteration:
            self._peek = None

        return value

    def skip(self):
        try:
            self.next()
        except:
            pass
        return self


def lookahead(fn):
    def wrapped(*args):
        return Lookahead(fn(*args))
    return wrapped


class Token:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.value == other.value
        else:
            return self.value == other

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def isa(self, ty):
        return isinstance(self, ty)


class Ident (Token): pass
class Num (Token): pass
class Char (Token): pass
class Op (Token): pass


handlers = [
    (Op, re.compile('[-+/*^]')),
    (Ident, re.compile('[a-zA-Z_][a-zA-Z0-9_]*')),
    (Num, re.compile('[0-9]+')),
]


@lookahead
def tokenize(string):
    while True:
        string = string.lstrip()
        for handler, pattern in handlers:
            match = pattern.match(string)
            if match:
                yield handler(match.group(0))
                string = string[match.end():]
                break
        else:
            if not string:
                return

            yield Char(string[0])
            string = string[1:]


class AST:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return str(self.value.value)


class NumAST (AST): pass
class IdentAST (AST): pass


class BinOpAST (AST):
    def __init__(self, lhs, op, rhs):
        self.lhs, self.op, self.rhs = lhs, op, rhs

    def __repr__(self):
        return "{}({}, {}, {})".format(
            self.__class__.__name__,
            self.lhs,
            self.op,
            self.rhs,
        )

    def __str__(self):
        return "({} {} {})".format(self.lhs, self.op.value, self.rhs,)


def parse_primary(tokens):
    if tokens.peek() == '(':
        return parse_expr(tokens.skip())
    elif tokens.peek().isa(Num):
        return NumAST(tokens.next())
    elif tokens.peek().isa(Ident):
        return IdentAST(tokens.next())
    return tokens.next()


precedence = {
    '^': 3,
    '*': 2,
    '/': 2,
    '+': 1,
    '-': 1,
}


def parse_binop_rhs(tokens, lhs, op):
    expr = parse_primary(tokens)
    if not tokens.peek() or not tokens.peek().isa(Op):
        return expr
    next_op = tokens.peek()
    prec = precedence[op.value]
    next_prec = precedence[next_op.value]
    if next_prec > prec:
        rhs = parse_binop_rhs(tokens.skip(), expr, next_op)
        return BinOpAST(expr, next_op, rhs)
    return expr


def parse_expr(tokens):
    expr = parse_primary(tokens)
    while tokens.peek() and tokens.peek().isa(Op):
        op = tokens.next()
        rhs = parse_binop_rhs(tokens, expr, op)
        expr = BinOpAST(expr, op, rhs)
    if tokens.peek() == ')':
        tokens.next()
        return expr
    return expr


def compile(ast):
    pass


def interp(bytecode):
    pass


tests = [
    "(a^2 + b^2)^(1/2)",
    "a^b^c^d",
    "a - b - c - d",
    "a + b * c - d",
]
print('-'*32)
for test in tests:
    tokens = tokenize(test)
    expr = parse_expr(tokens)
    print(test)
    print(expr)
    print('-'*32)
