# tests/test_functions.py

import math
from coordle.functions import build_function, FunctionParseError


def test_build_function_basic():
    f = build_function("2*x + 3")
    assert f(0) == 3
    assert f(1) == 5


def test_build_function_with_math():
    f = build_function("sin(x)")
    assert abs(f(0) - 0.0) < 1e-9
    assert abs(f(math.pi/2) - 1.0) < 1e-6


def test_disallowed_name():
    try:
        build_function("y + 1")
    except FunctionParseError:
        assert True
    else:
        assert False
