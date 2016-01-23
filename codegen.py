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
        fn_code = stmt.codegen()
        if isinstance(stmt, bcast.Fn):
            functions.append(fn_code)
        else:
            code.extend(fn_code)
    return functions, code
