import codegen


class AST:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return str(self.value.value)

    def label(self, env):
        return self


class Num (AST):
    def codegen(self):
        return [codegen.PushNum(self.value.value)]


class NameLabel (AST):
    def codegen(self):
        return [codegen.LoadLocal(self.value)]

    def __repr__(self):
        return "NameLabel({})".format(self.value)

    def __str__(self):
        return "[{}]".format(self.value)


class Ident (AST):
    def label(self, env):
        if self.value.value not in env[1]:
            raise Exception("Variable `{}` is undefined".format(
                self.value.value
            ))
        return NameLabel(env[1][self.value.value])


class BinOp (AST):
    def __init__(self, lhs, op, rhs):
        self.lhs, self.op, self.rhs = lhs, op, rhs

    def __repr__(self):
        return "{}({}, {}, {})".format(
            self.__class__.__name__,
            self.lhs,
            self.op,
            self.rhs,
        )

    def __str__(self):
        return "({} {} {})".format(self.lhs, self.op.value, self.rhs,)

    def codegen(self):
        code = self.lhs.codegen()
        code.extend(self.rhs.codegen())
        code.append(codegen.MathOp(self.op.value))
        return code

    def label(self, env):
        self.lhs = self.lhs.label(env)
        self.rhs = self.rhs.label(env)
        return self


class Assignment (AST):
    def __init__(self, name, expr):
        self.name, self.expr = name, expr

    def __repr__(self):
        return "Assignment({}, {})".format(self.name, self.expr)

    def __str__(self):
        return "{} = {}".format(self.name, self.expr)

    def codegen(self):
        code = self.expr.codegen()
        code.append(codegen.StoreLocal(self.name.value))
        return code

    def label(self, env):
        if self.name.value.value not in env[1]:
            env[1][self.name.value.value] = env[0]
            env[0] += 1
        self.name = self.name.label(env)
        self.expr = self.expr.label(env)
        return self


class Return (AST):
    def codegen(self):
        code = self.value.codegen()
        code.append(codegen.Return())
        return code

    def __str__(self):
        return "return {}".format(self.value)

    def label(self, env):
        self.value = self.value.label(env)
        return self
