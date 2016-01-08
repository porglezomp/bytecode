class Lookahead:
    """
    Wrap a generator to include a single object of lookahead.
    Will return None if you peek() at a completed generator
    """
    def __init__(self, gen):
        self.gen = gen
        self.done = False
        try:
            self._peek = self.gen.next()
        except StopIteration:
            self._peek = None
            self.done = True

    def peek(self):
        return self._peek

    def __iter__(self):
        return self

    def next(self):
        value = self._peek
        if self.done:
            raise StopIteration

        try:
            self._peek = self.gen.next()
        except StopIteration:
            self._peek = None
            self.done = True

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
