import re
from lookahead import lookahead


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
