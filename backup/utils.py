'''Some utils functions'''

from enum import Enum
from functools import wraps
from inspect import getfullargspec

def seq_run(functions):
    '''Run a list of functions sequentially'''
    for func, args in functions:
        func(*args)

def async_run(functions):
    '''Run a list of functions in async'''
    raise NotImplementedError()

def convert_enum(func):
    '''Automatically convert the input data to match the enum.
    :raises ValueError: If the value to be converted is no in the enum in the type hint.
    Example:
    .. code-block:: python
    class MyEnum(Enum):
        A = 0
        B = 1

    @convert_enum
    def myfunc(e: MyEnum):
        if isinstance(e, MyEnum.A):
            print('a')
        elif isinstance(e, MyEnum.B):
            print('b')
    '''
    @wraps(func)
    def decorator(*args, **kwargs):
        argspec = getfullargspec(func)
        args = list(args)
        print(func.__annotations__)
        print(args)
        print(kwargs)
        for key, myclass in func.__annotations__.items():
            if issubclass(myclass, Enum):
                try:
                    index = argspec.args.index(key)
                    value = args[index]
                except IndexError:
                    index = None
                    value = kwargs[key]
                enum_value = myclass(value)
                if index is not None:
                    args[index] = enum_value
                else:
                    kwargs[key] = enum_value
        print(args)
        print(kwargs)
        args = tuple(args)
        return func(*args, **kwargs)
    return decorator
