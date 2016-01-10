from __future__ import print_function
import codegen


ops = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    '^': lambda a, b: a ** b,
}


def interp(bytecode):
    data_stack = []
    local_stack = []
    for instr in bytecode:
        if instr.isa(codegen.PushNum):
            data_stack.append(instr.value)
        elif instr.isa(codegen.LoadLocal):
            addr = instr.value
            value = local_stack[addr]
            data_stack.append(value)
        elif instr.isa(codegen.StoreLocal):
            addr = instr.value
            value = data_stack.pop()
            if addr >= len(local_stack):
                extra_needed = len(local_stack) - addr + 1
                local_stack.extend([None]*extra_needed)
            local_stack[addr] = value
        elif instr.isa(codegen.MathOp):
            rhs = data_stack.pop()
            lhs = data_stack.pop()
            operation = ops[instr.value]
            data_stack.append(operation(lhs, rhs))
        elif instr.isa(codegen.Return):
            return data_stack.pop()
