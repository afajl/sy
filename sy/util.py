import sys
import time
import traceback
import cPickle as pickle

import sy.log

log = sy.log._new('sy.util')
 

#def fail(*args, **kwargs):
    #kwargs['exitcode'] = kwargs.get('exitcode', 1)
    #exit(*args, **kwargs)

#def exit(*args, **kwargs):
    #kwargs['file'] = kwargs.get('file', sys.stderr)
    #if args is not None:
        #sy.out(*args, **kwargs)
    #sys.exit(kwargs.get('exitcode', 0))


def memoize(f):
    ''' Function decorator that caches return values
    
    If the decorated function is called with the same arguments a cached
    response is returned. 
    This is useful for functions that does system calls, like talking 
    over the network or accessing the filesystem and whose value 
    wont be changed during the lifetime of the process::
    
        @sy.util.memoize
        def uname(arg):
            print 'Getting uname', arg
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



class retry(object):
    ''' Decorator for retrying function if exception occurs::

        @sy.util.retry
        def errorprone():
            raise Exception('fail')
 
    .. note:: Hides all raised exceptions except the last one.


    :arg tries: Num tries
    :arg exceptions: Exceptions to catch
    :arg delay: Wait between retries


    Copied from Peter Hoffmann: 
        http://peter-hoffmann.com/2010/retry-decorator-python.html

    .. todo:: Not tested

    '''   
    default_exceptions = (Exception)
    def __init__(self, tries, exceptions=None, delay=0):
        self.tries = tries
        if exceptions is None:
            exceptions = Retry.default_exceptions
        self.exceptions = exceptions
        self.delay = delay

    def __call__(self, f):
        def fn(*args, **kwargs):
            exception = None
            for _ in range(self.tries):
                try:
                    return f(*args, **kwargs)
                except self.exceptions, e:
                    log.debug('Retry, exception: ' +str(e))
                    time.sleep(self.delay)
                    exception = e
            #if no success after tries, raise last exception
            raise exception
        return fn

   
