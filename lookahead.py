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
