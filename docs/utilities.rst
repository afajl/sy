=====================
Logging and utilities
=====================

Logging - sy.log
================
This module allows you to very fast set up rotating file logs, log
and forget::

    import sy1 as sy

    # Set up log file at /var/my.log
    sy.log.to_file('/var/my.log')

    # Log a warning
    sy.log.warning('A warning')
 

You can add as many loggers as you want::

    import sy1 as sy

    # A file that contains all loglevels
    sy.log.to_file('/var/debug.log', level='debug')

    # Syslog only get severity info or higher
    sy.log.to_syslog(level='info')

    # Another file containing warnings or worse
    sy.log.to_file('/var/warn.log', level='warning')

    # Errors go to the screen to
    sy.log.to_screen(level='error')


    # This will be logged to debug.log, warn.log and syslog
    sy.log.warning('A log message')

    # This will be logged to all destinations
    sy.log.error('Another log message')


If you want to place a log file in the same directory as the script you can use 
the ``__file__`` variable::

    import sy1 as sy
    import os.path

    # Get the dir where this script is located and 
    # make it an absolute path
    script_dir = os.path.abspath(os.path.dirname(__file__))

    # Create a log file named ``script.log``
    sy.log.to_file(os.path.join(script_dir, 'script.log'))




The different levels are (in order of severity):

.. function:: sy.log.debug(msg)
.. function:: sy.log.info(msg)
.. function:: sy.log.warning(msg)
.. function:: sy.log.error(msg)
.. function:: sy.log.critical(msg)
.. function:: sy.log.exception(msg)

    Exception info is added to the message. This function
    should only be called from an exception handler.

    See the standard library :mod:`logging` for more information.


sy.log content
--------------
.. automodule:: sy.log

    .. autofunction:: sy.log.to_file(path, level='info', format='<time> <file> <level> <msg>', max_size=10, keep=5)

    .. autofunction:: sy.log.to_screen(level='info', format='<time> <file> <level> <msg>')
    .. autofunction:: sy.log.to_syslog(level='info', facility='user', format='<time> <file> <level> <msg>', address=None)


 
Showing output - sy.out
=======================

Its a good idea to use :func:`sy.out` to print to the screen.
The method allows you to log output to a file at the same time
and make it easy to implement a quiet mode::

    import sy1 as sy

    # Write to the screen
    sy.out('Hi', name)
    Hi john

    # Separate strings with ','
    sy.out('Hi', name, sep=',')
    Hi,john

    # Dont output newlines
    sy.out('Hi', name, end='')
    sy.out('... and bye')
    Hi,john... and bye

    # Set up a log file, and log with level 'info'
    sy.log.to_file('/tmp/hi.log')
    sy.out('Hi', name, log='info')
    Hi,john\\n

    # Ok we logged it
    sy.path.slurp('/tmp/hi.log')
    100723-05:36:04 myscript.py INFO Hi, john 

    # Write to stderr
    import sys
    sy.out('Hi', name, file=sys.stderr)
    Hi john
 
    # Shut up
    sy.log.shut_up()
    sy.out('Hi', name)

.. autofunction:: sy.out(*args, file=sys.stdout, sep=' ', end='\n', log=None)
.. autofunction:: sy.log.shut_up




Exceptions
==========

.. automodule:: sy1

  .. autoexception:: sy.Error
  .. autoexception:: sy.UserError
  .. autoexception:: sy.CommandError
  .. autoexception:: sy.CommandTimeoutError


Utilities
=========

.. automodule:: sy.util
   :members:
