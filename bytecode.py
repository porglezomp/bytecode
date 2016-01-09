from __future__ import print_function

from lexer import tokenize
from bcparser import parse
from codegen import codegen


tests = [
    "(3^2 + 4^2)^(1/2)",
    "a = 2; b = 2; c = 2; d = 2; a^b^c^d",
    "a = 2; b = 4; c = 3; d = 1; a - b - c - d",
    "4 + 12.5 * 3 - 18",
    "a = 1 + 2 ; b = a - 2 ; c = a * b",
]

print('-'*32)
for test in tests:
    tokens = tokenize(test)
    ast = parse(tokens)
    stack = codegen(ast)
    for statement in ast:
        print(statement)
    print('= '*16)
    for item in stack:
        print(item)
    print('-'*32)
