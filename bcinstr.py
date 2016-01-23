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
        '>': ('GT', 6),
        '<': ('LT', 7),
        '<=': ('LTE', 8),
        '>=': ('GTE', 9),
        '==': ('EQ', 10),
        '!=': ('NE', 11),
        '&&': ('AND', 12),
        '||': ('OR', 13),
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


class Branch(Instr):
    def __str__(self):
        return pad("BRANCH", 15) + str(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 7, self.value)


class CondBranch(Instr):
    def __init__(self, true_loc, false_loc):
        self.true_loc = true_loc
        self.false_loc = false_loc

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.true_loc, self.false_loc)

    def __str__(self):
        return (pad("COND_BRANCH", 15) + str(self.true_loc) +
                ' ' + str(self.false_loc))

    def to_bytecode(self):
        return struct.pack('<Bhh', 8, self.true_loc, self.false_loc)
