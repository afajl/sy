
from sy._internal import platform_module

__all__ = ('Interface', 'addif', 'all', 'check', 'configure', 'find', 'get',
           'refresh', 'unconfigure')
 
platforms = [
    (['Solaris', '2.10'], 'solaris10'),
]

platform_module(__name__, platforms, interface=__all__)

