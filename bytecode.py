from __future__ import print_function

from lexer import tokenize
from bcparser import parse
from codegen import codegen


tests = [
    "(a^2 + b^2)^(1/2)",
    "a^b^c^d",
    "a - b - c - d",
    "a + b * c - d",
    "a = 1 + 2 ; b = a - 2 ; c = a * b",
]

print('-'*32)
for test in tests:
    tokens = tokenize(test)
    ast = parse(tokens)
    # stack = codegen(ast)
    # for item in stack:
    #     print(item)
    for statement in ast:
        print(statement)
    print('-'*32)
