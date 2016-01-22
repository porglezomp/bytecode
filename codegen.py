import struct
import bcast


def pad(string, width):
    return string + " " * (width - len(string))


class Code:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)

    def isa(self, ty):
        return isinstance(self, ty)


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


class Return (Code):
    def __init__(self):
        pass

    def __repr__(self):
        return "Return"

    def __str__(self):
        return 'RETURN'

    def to_bytecode(self):
        return struct.pack('<Bi', 5, 0)


class Call (Code):
    def __str__(self):
        return 'CALL {}'.format(self.value)

    def to_bytecode(self):
        return struct.pack('<Bi', 6, self.value)


def codegen(ast):
    code = []
    env = bcast.Env()
    functions = []
    for stmt in ast:
        if isinstance(stmt, bcast.Fn):
            env.declare_function(stmt)

    for stmt in ast:
        stmt.label(env)
        code = stmt.codegen()
        if isinstance(stmt, bcast.Fn):
            functions.append(code)
        else:
            code.extend(code)
    return functions, code
