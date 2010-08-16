import sys
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
        

    The decorator pickles the arguments and uses the that as the cache key.
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


