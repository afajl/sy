'''
:synopsis: Logging management

.. todo:: Create and document log handling

.. moduleauthor: Paul Diaconescu <p@afajl.com>
''' 
import logbook

loggers = logbook.LoggerGroup()
loggers.disabled = True

def _new(name):
    log = logbook.Logger(name)
    loggers.add_logger(log)
    return log

