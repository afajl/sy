
import logging
import logging.handlers
import sys
import inspect
import os.path
import sy

_quiet = False

_logformat_screen = logging.Formatter('%(levelname)s: %(message)s') 
_logformat_file = logging.Formatter(
                    '%(asctime)s %(name)s %(levelname)s %(message)s', 
                    '%y%m%d-%H:%M:%S')
def _get_name(stacklevel=3):
    ''' Get the module or script name of the caller '''
    res = inspect.stack()[stacklevel][0].f_globals['__name__']
    if res == '__main__':
        res = os.path.basename(sys.argv[0])
    if not res:
        res = 'root'
    return res

def _log(severity, message, *args, **kwargs):
    name = _get_name()
    logger = logging.getLogger(name)
    #if not logger.handlers:
    #    to_screen()
    getattr(logger, severity)(message, *args, **kwargs)

def _level_logger(severity):
    ''' wrapper function to create logging functions for different levels '''
    def f(message, *args, **kwargs):
        _log(severity, message, *args, **kwargs)
    return f

debug = _level_logger('debug') 
info = _level_logger('info') 
warning = _level_logger('warning')
warn = warning
error = _level_logger('error')
critical = _level_logger('critical')
exception = _level_logger('exception')


# _______________________________
# Out function

def out(*args, **kwargs):
    ''' Write out strings and optionally log

    This function tries to mimic the new print function in python 3.
   
    :arg file: File to write to. Default ``stdout``
    :arg sep: Separator to use between arguments, default a space
    :arg end: What character to end output with, default a newline
    :arg log: Log the message with this severity.
    '''
    file = kwargs.get('file', sys.stdout)
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    log = kwargs.get('log', None)

    out = sep.join(args)
    if not _quiet:
        file.write(out + end)
    if log is not None:
        _log(log, out)


def shut_up():
    ''' Makes :func:`sy.out` quiet. Logentries are still written '''
    global _quiet
    _quiet = True
 


# _______________________________
# Setup loggers

def to_syslog(facility='user', level='error', format=_logformat_file, 
              address=None):
    ''' Log messages to syslog 

    Send log messages from the sy.log.<level> functions syslog.

    :arg address: Address where syslog is listening or device to write to. 
                  List with two values, (address, port). 
                  Default depends on platform.
    :arg facility: Facility to log to, default "user". Available facilities
                   are: auth, authpriv, cron, daemon, kern, lpr, mail, news
                   security, syslog, user, uucp, local0-7
    :arg level: See :func:`sy.log.to_file`, default is 'error' 
    '''
    if sys.platform == 'darwin':
        address = '/var/run/syslog'
    else:
        address = ('localhost', 514) 

    handler = logging.handlers.SysLogHandler(address, facility) 
    _addhandler(handler, format, level)

def to_screen(level='info', format=_logformat_screen):
    ''' Log messages to the screen
    
    Send log messages from the sy.log.<level> functions to stderr

    :arg level: See :func:`sy.log.to_file`, default is 'info' 
    :arg format: See :func:`sy.log.to_file` 
    '''
    handler = logging.StreamHandler() 
    _addhandler(handler, format, level)


def to_file(path, level='info', format=_logformat_file,
            max_size=10, keep=5):
    ''' Log messages to a log file

    Send log messages from the sy.log.<level> functions to a file.

    The logfile is by default rotated after 10 Mb and 5 logfiles are kept.

    :arg level: Send only log messages of this level and above to this file. 
                Possible values (in order of severity) are:
                debug, info, warning, error, critical. 
                Default is info.
    :arg format: Set format of log lines. 
    :arg max_size: How large the log file is allowed to grow before being 
                     rotated. Size in megabytes, default 10
    :arg keep: How many log files to keep, default 5. 
    '''

    handler = logging.handlers.RotatingFileHandler(path,
                                    maxBytes=max_size * 1024 * 1024, 
                                    backupCount=keep)
    _addhandler(handler, format, level)


def _addhandler(handler, format, level):
    level = getattr(logging, level.upper(), None)
    if level is None:
        raise AssertionError('Unknown loglevel specified')
    handler.setFormatter(format)
    handler.setLevel(level)

    # add handler to root logger
    rootlogger = logging.getLogger()
    rootlogger.setLevel(logging.NOTSET)
    rootlogger.addHandler(handler)





