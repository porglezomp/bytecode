import re
from lookahead import lookahead


class Token(object):
    """
    A Token represents the results of the lexing process.

    The token class is a container that implements generic functions that
    work generically for subclasses. To add a new token type, an empty subclass
    is usually sufficient.
    """
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        """
        Allows comparing to other tokens, as well as values of whatever type
        the token contains. This means that Char('a') == 'a', and Num(2) == 2.
        """
        if isinstance(other, Token):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        return not self == other

    # This is my favorite trick, use the __class__.__name__ to format the repr,
    # so that subclasses automatically work correctly.
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def isa(self, typ):
        """
        Sugar for isinstance()
        """
        return isinstance(self, typ)


class Num(Token):
    def __init__(self, value):
        self.value = float(value)

class Ident(Token): pass
class Char(Token): pass
class Op(Token): pass
class Sep(Token): pass
class Keyword(Token): pass


# The handlers are pairs of constructors and regular expressions. When a
# regular expression matches, that constructor will be called and the
# matched text with be consumed.
HANDLERS = [
    # None means skip
    (lambda _: None, re.compile(r'#.*')),
    (Keyword, re.compile(r'return|fn')),
    (Op, re.compile(r'-|\+|/|\*|\^|<=?|>=?|==|!=|&&|\|\|')),
    (Ident, re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
    (Num, re.compile(r'[0-9]+\.?[0-9]*')),
    (Sep, re.compile(r';')),
]


@lookahead
def tokenize(string):
    while True:
        # Strip any leading whitespace
        string = string.lstrip()
        for handler, pattern in HANDLERS:
            match = pattern.match(string)
            if match:
                value = handler(match.group(0))
                # If the handler returns None, then don't emit a token
                if value is not None:
                    yield handler(match.group(0))
                # Consume a portion of the string
                string = string[match.end():]
                # Don't try any further patterns
                break
        else:
            # If no pattern matched, and the string is empty, we're done.
            if not string:
                return

            # As a last resort, just emit the first character in the
            # text as a token.
            yield Char(string[0])
            string = string[1:]
