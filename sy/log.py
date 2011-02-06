'''
:synopsis: Logging management

.. todo:: Create and document log handling

.. moduleauthor: Paul Diaconescu <p@afajl.com>
''' 

try:
    import logbook
    from logbook import Logger
    logbook_enabled = True
except ImportError:
    logbook_enabled = False
    class Logger(object):
        def __init__(self, name, level=0):
            self.name = name
            self.level = level
            debug = info = warn = warning = notice = error = exception = \
                critical = log = lambda *a, **kw: None


if logbook_enabled:
    loggers = logbook.LoggerGroup()
    loggers.disabled = True

def _new(name):
    log = Logger(name)
    if logbook_enabled:
        loggers.add_logger(log)
    return log

