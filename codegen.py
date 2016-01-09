def pad(string, width):
    return string + " " * (width - len(string))


class Code:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)


class PushNum (Code):
    def __str__(self):
        return pad("PUSH_NUM", 15) + str(self.value)


class LoadLocal (Code):
    def __str__(self):
        return pad("LOAD_LOCAL", 15) + str(self.value)


class StoreLocal (Code):
    def __str__(self):
        return pad("STORE_LOCAL", 15) + str(self.value)


class MathOp (Code):
    op_names = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV',
        '^': 'EXP',
    }

    def __str__(self):
        return 'OP_' + MathOp.op_names[self.value]


def codegen(ast):
    code = []
    env = [0, {}]
    for line in ast:
        line.label(env)
        code.extend(line.codegen())
    return code
