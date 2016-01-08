from __future__ import print_function

from lexer import tokenize
from parser import parse
from codegen import codegen


tests = [
    "(a^2 + b^2)^(1/2)",
    "a^b^c^d",
    "a - b - c - d",
    "a + b * c - d",
]
print('-'*32)
for test in tests:
    tokens = tokenize(test)
    ast = parse(tokens)
    stack = codegen(ast)
    for item in stack:
        print(item)
    print('-'*32)
