import bcinstr


class Env(object):
    def __init__(self, parent=None):
        self.next_local = 0
        self.next_function = 0
        self.local_names = {}
        self.functions = {}

        self.parent = parent
        if self.parent is not None:
            self.next_function = self.parent.next_function
            self.functions = self.parent.functions

    def __str__(self):
        return "(functions: {fns}, local_names: {loc})".format(
            fns=self.functions, loc=self.local_names)

    def declare_function(self, fn):
        if fn.name.value in self.functions:
            raise Exception('function ' + fn.name.value +
                            ' already defined')

        self.functions[fn.name.value] = self.next_function
        self.next_function += 1
        fn.name = NameLabel(self.functions[fn.name.value])


class AST(object):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.value == other.value)

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
    def label(self, _):
        return self


class Num(AST):
    """
    Represents a literal number.
    """
    def codegen(self):
        return [bcinstr.PushNum(self.value.value)]


class Ident(AST):
    """
    Represents a variable.
    """
    def label(self, env):
        if self.value.value not in env.local_names:
            raise Exception("Variable `{}` is undefined".format(
                self.value.value
            ))
        return NameLabel(env.local_names[self.value.value])


class NameLabel(Ident):
    """
    A lower level replacement for a variable. Any two variables with the same
    label are the same variable, and the index of the label corresponds to the
    position of that variable stored on the local variables stack.
    """
    def codegen(self):
        return [bcinstr.LoadLocal(self.value)]

    def __str__(self):
        return "[{}]".format(self.value)


class BinOp(AST):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.lhs == other.lhs and self.op == other.op and
                self.rhs == other.rhs)

    # Generate the code for the left hand and right hand sides, then call the
    # operation. The stack model encodes expressions in RPN, so an expression
    # like (1 + 1) * 2 becomes (1 1 + 2 *).
    def codegen(self):
        code = self.lhs.codegen()
        code.extend(self.rhs.codegen())
        code.append(bcinstr.MathOp(self.op.value))
        return code

    # Recursively label both sides, with a shared environment.
    def label(self, env):
        self.lhs = self.lhs.label(env)
        self.rhs = self.rhs.label(env)
        return self


class Assignment(AST):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and self.expr == other.expr)

    def codegen(self):
        code = self.expr.codegen()
        code.append(bcinstr.StoreLocal(self.name.value))
        return code

    # Either replace the left hand side with a label from the environement,
    # or, if it's not present in the environment, bind it as a fresh name.
    # After labelling and binding the left hand side, label the expression.
    def label(self, env):
        if self.name.value.value not in env.local_names:
            env.local_names[self.name.value.value] = env.next_local
            env.next_local += 1
        self.name = self.name.label(env)
        self.expr = self.expr.label(env)
        return self


class Return(AST):
    """
    Represents return a result from the program.
    """
    def codegen(self):
        code = self.value.codegen()
        code.append(bcinstr.Return())
        return code

    def __str__(self):
        return "return {}".format(self.value)

    def label(self, env):
        self.value = self.value.label(env)
        return self


class Fn(AST):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and self.args == other.args and
                self.body == other.body)

    def codegen(self):
        code = []
        for i, _ in enumerate(self.args):
            code.append(bcinstr.StoreLocal(i))
        code = list(reversed(code))
        for line in self.body:
            code.extend(line.codegen())
        if not code[-1].isa(bcinstr.Return):
            code.append(bcinstr.PushNum(0))
            code.append(bcinstr.Return())
        return code

    def label(self, env):
        # Create a fresh environment local to the function,
        # with references to all functions in the global scope
        env = Env(env)

        for i, name in enumerate(self.args):
            env.local_names[name.value] = env.next_local
            self.args[i] = NameLabel(env.next_local)
            env.next_local += 1

        for i, line in enumerate(self.body):
            self.body[i] = line.label(env)

        return self


class Call(AST):
    def __init__(self, name, args):
        self.name, self.args = name, args

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.name, self.args,
        )

    def __str__(self):
        return "{}({})".format(self.name, ', '.join(self.args))

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and self.args == other.args)

    def codegen(self):
        code = []
        for arg in self.args:
            code.extend(arg.codegen())
        code.append(bcinstr.Call(self.name.value))
        return code

    def label(self, env):
        if self.name.value not in env.functions:
            raise Exception('{} not defined'.format(self.name.value))
        self.name = NameLabel(env.functions[self.name.value])
        self.args = [arg.label(env) for arg in self.args]
        return self


class IfElse(AST):
    def __init__(self, cond, if_block, else_block):
        self.cond = cond
        self.if_block, self.else_block = if_block, else_block

    def __repr__(self):
        return "{}({}, {}, {})".format(
            self.__class__.__name__,
            self.cond, self.if_block, self.else_block,
        )

    def __str__(self):
        if self.else_block is None:
            return "if {} {{\n  {}\n}}".format(
                self.cond,
                '  \n'.join(str(stmt) for stmt in self.if_block),
            )
        elif (len(self.else_block) == 1 and
              isinstance(self.else_block[0], IfElse)):
            return "if {} {{\n  {}\n}} else {}".format(
                self.cond,
                '  \n'.join(str(stmt) for stmt in self.if_block),
                str(self.else_block[0]),
            )
        else:
            return "if {} {{\n  {}\n}} else {{\n  {}\n}}".format(
                self.cond,
                '  \n'.join(str(stmt) for stmt in self.if_block),
                '  \n'.join(str(stmt) for stmt in self.else_block)
            )

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.cond == other.cond and
                self.if_block == other.if_block and
                self.else_block == other.else_block)

    def codegen(self):
        code = self.cond.codegen()
        if_code = []
        for stmt in self.if_block:
            if_code.extend(stmt.codegen())
        else_code = []
        if self.else_block is not None:
            for stmt in self.else_block:
                else_code.extend(stmt.codegen())
        if_code.append(bcinstr.Branch(len(else_code)))
        code.append(bcinstr.CondBranch(0, len(if_code)))
        code.extend(if_code)
        code.extend(else_code)
        return code

    def label(self, env):
        self.cond = self.cond.label(env)
        for stmt in self.if_block:
            stmt.label(env)
        if self.else_block is not None:
            for stmt in self.else_block:
                stmt.label(env)
        return self
