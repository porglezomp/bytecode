import bcast


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
