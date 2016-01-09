from lexer import Num, Ident, Op
import bcast


def parse_primary(tokens):
    if tokens.peek() == '(':
        return parse_expr(tokens.skip())
    elif tokens.peek().isa(Num):
        return bcast.Num(tokens.next())
    elif tokens.peek().isa(Ident):
        return bcast.Ident(tokens.next())
    raise Exception("Parse Error")


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
        lhs = bcast.BinOp(lhs, op, rhs)
    return lhs


def parse_expr(tokens, expr=None):
    if expr is None:
        expr = parse_primary(tokens)

    if not tokens.peek():
        return expr

    if tokens.peek().isa(Op):
        expr = parse_binop_rhs(tokens, expr, 0)
    if tokens.peek() == ')':
        tokens.skip()
    return expr


def parse_statement(tokens):
    expr = parse_primary(tokens)
    if tokens.peek() == '=':
        rhs = parse_expr(tokens.skip())
        return bcast.Assignment(expr, rhs)

    return parse_expr(tokens, expr)


def parse(tokens):
    statements = []
    while tokens.peek():
        statements.append(parse_statement(tokens))
        if tokens.peek() == ';':
            tokens.skip()

    return statements
