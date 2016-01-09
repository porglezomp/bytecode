class Code:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)


class PushNum (Code): pass
class LoadLocal (Code): pass
class StoreLocal (Code): pass
class MathOp (Code): pass


def codegen(ast):
    code = []
    env = [0, {}]
    for line in ast:
        line.label(env)
        code.extend(line.codegen())
    return code
