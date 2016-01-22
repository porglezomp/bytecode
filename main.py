#!/usr/bin/env python3
from __future__ import print_function

import argparse

from lexer import tokenize
from bcparser import parse
from codegen import codegen
from interpreter import interp


tests = [
    "(3^2 + 4^2)^(1/2)",
    "a = 2; b = 2; c = 2; d = 2; a^b^c^d",
    "a = 2; b = 4; c = 3; d = 1; a - b - c - d",
    "4 + 12.5 * 3 - 18",
    "a = 1 + 2 ; b = a - 2 ; c = a * b",
]


def compile_bytecode(name):
    with open(name, 'r') as f:
        text = f.read()
    tokens = tokenize(text)
    ast = parse(tokens)
    fns, stack = codegen(ast)
    return fns, stack


def output(code, name):
    code = [instr.to_bytecode() for instr in code]
    with open(name, 'wb') as f:
        f.write(b''.join(code))


def prettyprint(fns, code):
    fns = ['\n'.join(str(instr) for instr in fn) for fn in fns]
    fns.append('\n'.join(str(instr) for instr in code))
    return '\n\n'.join(fns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compile or interpret .math scripts.')

    parser.add_argument('filename', type=str,
                        help='the file to compile or interpret')
    parser.add_argument('-o, --out', dest='output', type=str,
                        help='the file to write compiled output to')
    parser.add_argument('-p, --pretty', dest='pretty',
                        action='store_true',
                        help='output pretty-printed code')

    args = parser.parse_args()

    fns, code = compile_bytecode(args.filename)
    if args.pretty:
        out = prettyprint(fns, code)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(out)
        else:
            print(out)
    elif args.output:
        output(code, args.output)
    else:
        result = interp(fns, code)
        print(result)
