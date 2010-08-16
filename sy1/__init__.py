# Allow access to all modules through the top-level module, ex:
#   import sy
#   sy.cmd.run(('ifconfig', '-a'))

__version__ = '1.0'

# add library to python path
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from sy1._internal import dynload_module


# So what is this?
# Since I wanted to create a simple interface where everything starts
# from sy. we would need to import everything in this file. That would
# mean that the whole library was imported even if the developer only
# wanted one function.
#
# With this hack we replace this module with a new one that imports
# modules and functions on demand when they are requested. If a user
# only wants things in sy.util only that module will be imported.
#
# This is copied from the werkzeug library with great respect and
# admiration
#
# Things that should live directly under sy.
objects = {
    'sy.exception':     ['Error', 'UserError', 'CommandError', 
                         'CommandTimeoutError'],
    'sy.log':           ['out'],
}

# Modules that should be accessible from sy.
modules = ('util', 'log', 'path', 'net', 'cmd', 'prompt') 


dynload_module(__name__, modules, objects)
 
