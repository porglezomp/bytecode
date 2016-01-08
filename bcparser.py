import codegen
from lexer import Num, Ident, Op


class AST:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return str(self.value.value)


class NumAST (AST):
    def codegen(self):
        return [codegen.PushNum(int(self.value.value))]


class IdentAST (AST):
    def codegen(self):
        return [codegen.LoadLocal(self.value.value)]


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

    def codegen(self):
        code = self.lhs.codegen()
        code.extend(self.rhs.codegen())
        code.append(codegen.MathOp(self.op.value))
        return code


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


def parse(tokens):
    return parse_expr(tokens)
