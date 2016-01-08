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


def tokenize(string):
    pass


def parse(tokens):
    pass


def compile(ast):
    pass


def interp(bytecode):
    pass
