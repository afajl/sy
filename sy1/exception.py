"""
sy.exception
------------
   :synopsis: Exceptions used by the library


.. moduleauthor: Paul Diaconescu <p@feedem.se>
"""

class Error(Exception):
    ''' Base exception for the sy  '''
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self)

    def __unicode__(self):
        return self.msg

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, str(self)) 

    __str__ = __unicode__

class UserError(Error):
    """ User supplied bad data """
    pass

class CommandError(Error):
    ''' Command failed error. Subclass of :exc:`Error`.
    
    .. attribute:: out

       The stdout collected from the command

    .. attribute:: err

       The stdout collected from the command

    .. attribute:: status
            
       The commands exit status

    .. attribute:: cmd

        The command that was run
    '''
    def __init__(self, msg, out=None, err=None, status=None, cmd=None):
        self.out = out
        self.err = err
        self.status = status
        self.cmd = cmd
        Error.__init__(self, msg)

class CommandTimeoutError(CommandError):
    ''' Command failed due to time out. Subclass of :exc:`CommandError`.
    
    .. attribute:: timeout

       The timeout that was exceeded

    '''
 
    def __init__(self, msg, timeout=None, *args, **kwargs):
        self.timeout = timeout
        CommandError.__init__(self, msg, *args, **kwargs)


