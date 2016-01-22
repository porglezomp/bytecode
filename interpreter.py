from __future__ import print_function
import codegen


ops = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    '^': lambda a, b: a ** b,
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
                extra_needed = addr - len(local_stack) + 1
                local_stack.extend([None]*extra_needed)
            local_stack[addr] = value
        elif instr.isa(codegen.MathOp):
            rhs = data_stack.pop()
            lhs = data_stack.pop()
            operation = ops[instr.value]
            data_stack.append(operation(lhs, rhs))
        elif instr.isa(codegen.Return):
            ret = data_stack.pop()
            if not call_stack:
                return ret
            else:
                data_stack.append(ret)
            local_stack = local_save.pop()
            code, ip = call_stack.pop()
        elif instr.isa(codegen.Call):
            local_save.append(local_stack)
            local_stack = []
            call_stack.append((code, ip))
            ip = -1
            code = fns[instr.value]
        else:
            raise Exception("Unsupported instruction " + instr)
        ip += 1
        if False:
            print('@@@')
            print('code', code)
            print('ip', ip)
            print('data', data_stack)
            print('local',  local_stack)
            print('stack', '[{}]'.format(
                ', '.join(str((Ellipsis, p)) for _, p in call_stack)))
            print('scopes', local_save)
            print()
