from __future__ import print_function

import sys

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


def compile(name):
    with open(name, 'r') as f:
        text = f.read()
    tokens = tokenize(text)
    ast = parse(tokens)
    stack = codegen(ast)
    return stack


def output(code, name):
    code = [instr.to_bytecode() for instr in code]
    with open(name, 'wb') as f:
        f.write(b''.join(code))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Name a file")
        exit(0)

    code = compile(sys.argv[1])
    if len(sys.argv) > 2:
        outfile = sys.argv[2]
        output(code, outfile)
    else:
        print(interp(code))
