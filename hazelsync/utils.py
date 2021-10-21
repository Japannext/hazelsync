'''Some utils functions'''

def seq_run(functions):
    '''Run a list of functions sequentially'''
    results = []
    for func, args in functions:
        results.append(func(*args))
    return results

def async_run(functions):
    '''Run a list of functions in async'''
    raise NotImplementedError()
