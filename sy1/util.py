import sys
import time
import traceback
import cPickle as pickle

import sy1 as sy


def fail(*args, **kwargs):
    kwargs['exitcode'] = kwargs.get('exitcode', 1)
    exit(*args, **kwargs)

def exit(*args, **kwargs):
    kwargs['file'] = kwargs.get('file', sys.stderr)
    if args is not None:
        sy.out(*args, **kwargs)
    sys.exit(kwargs.get('exitcode', 0))


def memoize(f):
    ''' Function decorator that caches return values
    
    If the decorated function is called with the same arguments a cached
    response is returned. 
    This is useful for functions that does system calls, like talking 
    over the network or accessing the filesystem and whose value 
    wont be changed during the lifetime of the process::
    
        @sy.util.memoize
        def uname(arg):
            sy.out('Getting uname', arg)
            return sy.cmd.outlines('uname -{}', arg)[0]

        uname('r')
        Getting uname r

        uname('s')
        Getting uname s

        uname('r') # cached value returned
        

    The decorator creates a pickle of the arguments and uses it as cache key.
    If the arguments cant be pickled it will throw a :exc:`pickle.PickleError`.
    '''
    cache = {}
    def g(*args, **kwargs):
        key = pickle.dumps( (args, kwargs) )
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]

    g.__doc__ = f.__doc__
    g.__name__ = f.__name__
    g.__dict__.update(f.__dict__)
    return g

def attempt_to(func, *args, **kwargs):
    ''' Try to execute a function until it succeeds

    The function should return a truthy value, or a tuple where 
    the first value is a bool indicating if the function was successfull::


        >>> import sy1 as sy
        >>> def ok_sometimes(a):
        ...     return True, 'Yes ' + a

        >>> ret = sy.util.attempt(ok_sometimes, 'success!') 
        >>> print ret
        Yes success!


    The ``attempt_to`` function tries to return a sane value to the caller.
  
    ==================  ===========
    Function returns    Caller sees
    ==================  ===========
    return True         True
    return True, 1      1
    return True, 1, 2   (1, 2)
    return 'foo'        'foo'
    return ""           (fails with :exc:`sy.Error` after all attempts)
    return False, 1, 3  (fails with :exc:`sy.Error` after all attempts)
    Exception           (fails with ``Exception`` after all attempts)
    ==================  ===========

    If the function raises an exception on the last attempt it propagates
    to the caller. Note that exceptions that occur before the last attempt
    are hidden.

    If the function does not succeed an :exc:`sy.Error` is raised.

    :arg func: Function to execute
    :arg attempts: Number of attempts, default 3
    :arg backoff: Sleep for attempt*backoff seconds between attempts, default 2
    '''
    attempts = kwargs.pop('attempts', 3)
    backoff = kwargs.pop('backoff', 2)

    for attempt in range(attempts):
        try:
            res = func(*args, **kwargs)
            if isinstance(res, tuple):
                l = len(res)
                if l == 0:
                    ok = ret = res # empty tuple is falsy
                elif l == 1:
                    ok = ret = res[0]
                elif l == 2:
                    ok, ret = res
                elif l > 2:
                    ok, ret = res[0], res[1:]
            else:
                ok = res
                ret = res
            if ok:
                return ret
        except:
            trace = ''.join(traceback.format_exception(*sys.exc_info()))
            sy.log.info('Function %s raised an exception: %s', func.__name__,
                        trace)
            if attempt+1 == attempts:
                raise 

        if backoff:
            time.sleep(attempt * backoff)
    else:
        raise sy.Error('Failed attempt to run %s after %d times' % (
                        func.__name__, attempts))


    
