from nose.tools import assert_raises, eq_
import sy.util

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
    
#def test_attempt_bad():
    #attempts = []
    #funbad = lambda: attempts.append(0) or False
    #try:
        #sy.util.attempt_to(funbad, backoff=0)
        #assert False, 'fun should fail'
    #except: pass
    #eq_(len(attempts), 3)

#def test_attempt_ok():
    #attempts = []
    #funok = lambda: attempts.append(0) or True
    #sy.util.attempt_to(funok, backoff=0)
    #eq_(len(attempts), 1)


#def test_attempt_tries():
    #attempts = []
    #funbad = lambda: attempts.append(0) or False
    #try:
        #sy.util.attempt_to(funbad, attempts=5, backoff=0)
        #assert False, 'fun should fail'
    #except: pass
    #eq_(len(attempts), 5)
 

#def test_attempt_ret():
    #def single(): return True, 'foo'
    #ret = sy.util.attempt_to(single)
    #eq_(ret, 'foo')

    #def mult(): return True, 'foo', 'bar'
    #ret = sy.util.attempt_to(mult)
    #eq_(ret, ('foo', 'bar'))

    #def truthy(): return 'foo'
    #ret = sy.util.attempt_to(truthy)
    #eq_(ret, 'foo')

    #def falsy(): return ''
    #try:
        #sy.util.attempt_to(truthy, backoff=0)
        #assert False, 'falsy should fail'
    #except: pass

    #def empty(): return ()
    #try:
        #sy.util.attempt_to(empty, backoff=0)
        #assert False, 'empty should fail'
    #except: pass
 
    #def true_tuple(): return (True,)
    #ret = sy.util.attempt_to(true_tuple)
    #eq_(ret, True)
 


#def test_attempt_exc():
    #attempts = []
    #def ex(): 
        #attempts.append(0)
        #raise RuntimeError()
    #try:
        #sy.util.attempt_to(ex, backoff=0)
        #assert False, 'ex should fail'
    #except RuntimeError:
       #pass
    #eq_(len(attempts), 3)

        
 
    

