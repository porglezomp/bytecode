import struct


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

    def to_bytecode(self):
        return struct.pack('<Bf', 1, self.value)


class LoadLocal (Code):
    def __str__(self):
        return pad("LOAD_LOCAL", 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 2, self.value)


class StoreLocal (Code):
    def __str__(self):
        return pad("STORE_LOCAL", 15) + str(self.value)

    def format(self):
        return ()

    def to_bytecode(self):
        return struct.pack('<Bi', 3, self.value)


class MathOp (Code):
    op_info = {
        '+': ('ADD', 1),
        '-': ('SUB', 2),
        '*': ('MUL', 3),
        '/': ('DIV', 4),
        '^': ('EXP', 5),
    }

    def __str__(self):
        return pad('OP_' + MathOp.op_info[self.value][0], 15)

    def to_bytecode(self):
        return struct.pack('<Bi', 4, MathOp.op_info[self.value][1])


def codegen(ast):
    code = []
    env = [0, {}]
    for line in ast:
        line.label(env)
        code.extend(line.codegen())
    return code
