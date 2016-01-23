import bcinstr


DEBUG = False
ops = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    '^': lambda a, b: a ** b,
    '>': lambda a, b: float(a > b),
    '<': lambda a, b: float(a < b),
    '>=': lambda a, b: float(a >= b),
    '<=': lambda a, b: float(a <= b),
    '==': lambda a, b: float(a == b),
    '!=': lambda a, b: float(a != b),
    '&&': lambda a, b: float(a and b),
    '||': lambda a, b: float(a or b),
}


def interp(fns, bytecode):
    code = bytecode
    ip = 0
    data_stack = []
    local_stack = []
    local_save = []
    call_stack = []
    while True:
        instr = code[ip]
        if DEBUG:
            print('@@@')
            print('code', code)
            print('ip', ip)
            print('instr', instr)
            print('data', data_stack)
            print('local',  local_stack)
            print('stack', '[{}]'.format(
                ', '.join(str((Ellipsis, p)) for _, p in call_stack)))
            print('scopes', local_save)
            print()

        if instr.isa(bcinstr.PushNum):
            data_stack.append(instr.value)
        elif instr.isa(bcinstr.LoadLocal):
            addr = instr.value
            value = local_stack[addr]
            data_stack.append(value)
        elif instr.isa(bcinstr.StoreLocal):
            addr = instr.value
            value = data_stack.pop()
            if addr >= len(local_stack):
                extra_needed = addr - len(local_stack) + 1
                local_stack.extend([None]*extra_needed)
            local_stack[addr] = value
        elif instr.isa(bcinstr.MathOp):
            rhs = data_stack.pop()
            lhs = data_stack.pop()
            data_stack.append(ops[instr.value](lhs, rhs))
        elif instr.isa(bcinstr.Return):
            if not call_stack:
                return data_stack.pop()
            local_stack = local_save.pop()
            code, ip = call_stack.pop()
        elif instr.isa(bcinstr.Call):
            local_save.append(local_stack)
            local_stack = []
            call_stack.append((code, ip))
            ip = -1
            code = fns[instr.value]
        elif instr.isa(bcinstr.Branch):
            ip += instr.value
        elif instr.isa(bcinstr.CondBranch):
            if data_stack.pop():
                ip += instr.true_loc
            else:
                ip += instr.false_loc
        else:
            raise Exception("Unsupported instruction " + instr)
        ip += 1
