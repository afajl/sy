from nose.tools import assert_raises
import sy1 as sy

def test_memoize_simple():
    called = [0]
    @sy.util.memoize
    def f():
        called[0] += 1
        return 42

    x1 = f()
    x2 = f()
    assert x1 == x2 == 42
    assert called[0] == 1

def test_memoize_unhashable():
    called = [0]
    @sy.util.memoize
    def f(a, b=None):
        called[0] += 1
        return list(a)[0] + b

    x1 = f((1,), b=2)
    x2 = f((1,), b=2)
    y = f([1], b=2)
    z = f([1], b=2)
    assert x1 == x2 == y == z == 3
    assert called[0] == 2

def test_memoize_kwargs():
    called = [0]
    @sy.util.memoize
    def f(a=1, b=2, c=3):
        called[0] += 1
        return a + b + c

    x = f(a=1, b=2, c=3)
    y = f(c=3, a=1, b=2)
    z = f()
    assert x == y == z == 6
    assert called[0] == 2
    



