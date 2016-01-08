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


operator_table = {
    '^': (3, 'R'),
    '*': (2, 'L'),
    '/': (2, 'L'),
    '+': (1, 'L'),
    '-': (1, 'L'),
}
precedence = {k: v for k, (v, _) in operator_table.iteritems()}
associativity = {k: v for k, (_, v) in operator_table.iteritems()}


def parse_binop_rhs(tokens, lhs, prec):
    look = tokens.peek()
    while (look and look.isa(Op) and precedence[look.value] >= prec):
        op = tokens.next()
        rhs = parse_primary(tokens)
        op_prec = precedence[op.value]
        look = tokens.peek()
        while (look and look.isa(Op) and
               (precedence[look.value] > op_prec or
                associativity[look.value] == 'R' and
                precedence[look.value] >= op_prec)):
            op_prec = precedence[look.value]
            rhs = parse_binop_rhs(tokens, rhs, op_prec)
            look = tokens.peek()
        lhs = BinOpAST(lhs, op, rhs)
    return lhs


def parse_expr(tokens):
    expr = parse_primary(tokens)
    if not tokens.peek():
        return expr

    if tokens.peek().isa(Op):
        expr = parse_binop_rhs(tokens, expr, 0)
    if tokens.peek() == ')':
        tokens.skip()
    return expr


class Code:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)


class PushNum (Code): pass
class LoadLocal (Code): pass
class StoreLocal (Code): pass
class MathOp (Code): pass


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
