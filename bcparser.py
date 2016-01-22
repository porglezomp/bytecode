from lexer import Num, Ident, Op, Keyword
import bcast


def parse_primary(tokens):
    if tokens.peek() == '(':
        expr = parse_expr(tokens.skip())
        assert tokens.next() == ')'
        return expr

    elif tokens.peek().isa(Num):
        return bcast.Num(tokens.next())
    elif tokens.peek().isa(Ident):
        name = tokens.next()
        if tokens.peek() == '(':
            args = parse_args(tokens)
            return bcast.Call(name, args)
        else:
            return bcast.Ident(name)
    raise Exception("Parse Error, got {}, expecting a number, "
                    "variable, or parenthesis.".format(
                        tokens.peek()
                    ))


def parse_args(tokens):
    assert tokens.next() == '('
    args = []
    while tokens.peek() != ')':
        args.append(parse_expr(tokens))
        if tokens.peek() == ',':
            tokens.skip()

    assert tokens.next() == ')'
    return args


operator_table = {
    '^': (100, 'R'),
    '*': (80, 'L'),
    '/': (80, 'L'),
    '+': (60, 'L'),
    '-': (60, 'L'),
    '<': (50, 'L'),
    '>': (50, 'L'),
    '<=': (50, 'L'),
    '>=': (50, 'L'),
    '==': (40, 'L'),
    '!=': (40, 'L'),
    '&&': (30, 'L'),
    '||': (20, 'L'),
}

precedence = {k: v for k, (v, _) in operator_table.items()}
associativity = {k: v for k, (_, v) in operator_table.items()}


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
    return expr


def parse_statement(tokens):
    if tokens.peek().isa(Keyword):
        if tokens.peek() == 'return':
            expr = parse_expr(tokens.skip())
            return bcast.Return(expr)
        elif tokens.peek() == 'fn':
            name = tokens.skip().next()
            assert name.isa(Ident)
            assert tokens.next() == '('
            args = []
            while tokens.peek().isa(Ident):
                args.append(tokens.next())
                if tokens.peek() == ',':
                    tokens.skip()
            assert tokens.next() == ')'
            assert tokens.next() == '{'
            statements = []
            while tokens.peek() != '}':
                if tokens.peek() == '}':
                    break
                statements.append(parse_statement(tokens))
                if tokens.peek() == ';':
                    tokens.skip()
            assert tokens.next() == '}'
            return bcast.Fn(name, args, statements)
        raise Exception("Unimplemented keyword `{}`".format(
            tokens.peek().value
        ))
    else:
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
