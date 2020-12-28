def destruct_tuple(f):
    return lambda args: f(*args)
