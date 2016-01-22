import struct


def pad(string, width):
    return string + " " * (width - len(string))


class Instr(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)

    def isa(self, typ):
        return isinstance(self, typ)


class PushNum(Instr):
    def __str__(self):
        return pad("PUSH_NUM", 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bf', 1, self.value)


class LoadLocal(Instr):
    def __str__(self):
        return pad("LOAD_LOCAL", 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 2, self.value)


class StoreLocal(Instr):
    def __str__(self):
        return pad("STORE_LOCAL", 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 3, self.value)


class MathOp(Instr):
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


class Return(Instr):
    def __init__(self):
        pass

    def __repr__(self):
        return "Return"

    def __str__(self):
        return 'RETURN'

    def to_bytecode(self):
        return struct.pack('<Bi', 5, 0)


class Call(Instr):
    def __str__(self):
        return pad('CALL', 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 6, self.value)
