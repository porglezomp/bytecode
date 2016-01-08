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


def parse(tokens):
    pass


def compile(ast):
    pass


def interp(bytecode):
    pass


print(list(tokenize("(a^2 + b^2)^(1/2)")))
print(list(tokenize("10 - 9 * 3")))
