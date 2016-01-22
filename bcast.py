import codegen


class Env:
    def __init__(self, parent=None):
        self.parent = parent
        self.next_local = 0
        self.next_function = 0
        self._local_names = {}
        self._functions = {}

    def local_contains(self, item):
        if item in self._local_names:
            return True
        if self.parent is None:
            return False
        return self.parent.local_contains(item)

    def local_names(self, name):
        if name in self._local_names:
            return self._local_names[name]
        if self.parent is None:
            raise IndexError()
        return self.parent.local_names(name)

    def function_contains(self, item):
        if item in self._functions:
            return True
        if self.parent is None:
            return False
        return self.parent.function_contains(item)

    def function_names(self, name):
        if name in self._functions:
            return self._functions[name]
        if self.parent is None:
            raise IndexError()
        return self.parent.function_names(name)

    def declare_function(self, fn):
        if self.parent:
            self.parent.declare_function(fn.name)
        else:
            self._functions[fn.name.value] = self.next_function
            self.next_function += 1
            fn.name = NameLabel(self.function_names(fn.name.value))


class AST:
    """
    The AST base class handles everything necessary for a single-valued AST
    node. This means that most subclasses don't need to impelement __repr__,
    etc.
    """
    def __init__(self, value):
        self.value = value

    # Use the __class__.__name__ to print out the object appropriately for
    # subclasses.
    # You should overload this if you overload the constructor.
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def __str__(self):
        return str(self.value.value)

    # Every subclass should implement codegen.
    def codegen(self):
        raise Exception("Codegen unimplemented for {}".format(
            self.__class__.__name__
        ))

    # label() takes things with complex representations, like variables, and
    # introduces a simpler form that's more useful for the final compilation
    # steps. All variables are replaced by indices into the local variables
    # stack. In general though, most AST objects don't need to do anything
    # special.
    def label(self, env):
        return self


class Num (AST):
    """
    Represents a literal number.
    """
    def codegen(self):
        return [codegen.PushNum(self.value.value)]


class Ident (AST):
    """
    Represents a variable.
    """
    def label(self, env):
        if not env.local_contains(self.value.value):
            raise Exception("Variable `{}` is undefined".format(
                self.value.value
            ))
        return NameLabel(env.local_names(self.value.value))


class NameLabel (Ident):
    """
    A lower level replacement for a variable. Any two variables with the same
    label are the same variable, and the index of the label corresponds to the
    position of that variable stored on the local variables stack.
    """
    def codegen(self):
        return [codegen.LoadLocal(self.value)]

    def __str__(self):
        return "[{}]".format(self.value)


class BinOp (AST):
    """
    Represents a binary operation on two expressions. The lhs and rhs
    attributes represent the two expressions, and the op attribute
    stores the operator applied to them.
    """
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

    # Generate the code for the left hand and right hand sides, then call the
    # operation. The stack model encodes expressions in RPN, so an expression
    # like (1 + 1) * 2 becomes (1 1 + 2 *).
    def codegen(self):
        code = self.lhs.codegen()
        code.extend(self.rhs.codegen())
        code.append(codegen.MathOp(self.op.value))
        return code

    # Recursively label both sides, with a shared environment.
    def label(self, env):
        self.lhs = self.lhs.label(env)
        self.rhs = self.rhs.label(env)
        return self


class Assignment (AST):
    """
    Represents the creation and assignment of variables. The right hand side of
    the assignment is stored in the expr attribute. The AST is invalid if
    anything other than an Ident is stored in the name attribute.
    """
    def __init__(self, name, expr):
        assert isinstance(name, Ident)
        self.name, self.expr = name, expr

    def __repr__(self):
        return "Assignment({}, {})".format(self.name, self.expr)

    def __str__(self):
        return "{} = {}".format(self.name, self.expr)

    def codegen(self):
        code = self.expr.codegen()
        code.append(codegen.StoreLocal(self.name.value))
        return code

    # Either replace the left hand side with a label from the environement,
    # or, if it's not present in the environment, bind it as a fresh name.
    # After labelling and binding the left hand side, label the expression.
    def label(self, env):
        if not env.local_contains(self.name.value.value):
            env._local_names[self.name.value.value] = env.next_local
            env.next_local += 1
        self.name = self.name.label(env)
        self.expr = self.expr.label(env)
        return self


class Return (AST):
    """
    Represents return a result from the program.
    """
    def codegen(self):
        code = self.value.codegen()
        code.append(codegen.Return())
        return code

    def __str__(self):
        return "return {}".format(self.value)

    def label(self, env):
        self.value = self.value.label(env)
        return self


class Fn (AST):
    def __init__(self, name, args, body):
        self.name, self.args, self.body = name, args, body

    def __repr__(self):
        return "{}({}, {}, {})".format(
            self.__class__.__name__,
            self.name, self.args, self.body
        )

    def __str__(self):
        return "fn {name}({args}) {{\n{body}\n}}".format(
            name=self.name.value,
            args=', '.join(str(arg) for arg in self.args),
            body='\n'.join("  {};".format(stmt) for stmt in self.body),
        )

    def codegen(self):
        code = []
        for i, _ in enumerate(self.args):
            code.append(codegen.StoreLocal(i))
        code = list(reversed(code))
        for line in self.body:
            code.extend(line.codegen())
        return code

    def label(self, env):
        env = Env(env)
        if env.function_contains(self.name.value):
            raise Exception('function ' + self.name.value +
                            ' already defined')

        for i, name in enumerate(self.args):
            env._local_names[name.value] = env.next_local
            self.args[i] = NameLabel(env.next_local)
            env.next_local += 1

        for i, line in enumerate(self.body):
            self.body[i] = line.label(env)

        return self


class Call (AST):
    def __init__(self, name, args):
        self.name, self.args = name, args

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.name, self.args,
        )

    def __str__(self):
        return "{}({})".format(self.name, ', '.join(self.args))

    def codegen(self):
        code = []
        for arg in self.args:
            code.extend(arg.codegen())
        code.append(codegen.Call(self.name.value))
        return code

    def label(self, env):
        if not env.function_contains(self.name.value):
            raise Exception('{} not defined'.format(self.name.value))
        self.name = NameLabel(env.function_names(self.name.value))
        self.args = [arg.label(env) for arg in self.args]
        return self
