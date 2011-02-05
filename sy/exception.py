"""
sy.exception
------------
   :synopsis: Exceptions used by the library


.. moduleauthor: Paul Diaconescu <p@afajl.com>
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



