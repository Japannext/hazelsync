'''Test for utils functions'''

from enum import Enum

import pytest

from backup.utils import convert_enum

def test_convert_enum():

    class MyEnum(Enum):
        A = 0
        B = 1

    @convert_enum
    def func(e: MyEnum):
        return e

    assert func(0) == MyEnum.A
    assert func(1) == MyEnum.B
    with pytest.raises(ValueError):
        func(3)
