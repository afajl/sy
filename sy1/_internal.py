import sys
from types import ModuleType
import platform
import re

class _Missing(object):
    def __repr__(self):
        return 'no value'
    
    def __reduce__(self):
        return '_missing'

_missing = _Missing()

def platform_select(options, test_platform=()):
    ''' Find the current platform 

    Matches the output from platform.system_alias, ``system``, ``release``
    and ``version`` against 0-3 regular expressions and returns the first
    match.

    Given that the platform is (from :func:`platform.system_alias`)::
        ('Linux', '2.6.9-11.ELsmp', '#1 SMP Fri May 20 18:26:27 EDT 2005')

    A list of options like this:
        [
            # Match system and release
            (['Linux', '2.6.\d\d.*'], 'linux_new'),

            # Match only system
            (['Linux'] , 'linux_generic'),
        ]

    Would return ``linux_generic``.

    :arg options: List of platforms to match against, every entry must have
                  the format::
                  (list([system match, [release match, [version match]]]), <return value>)

                  If the list is empty all platforms would match.
                  If more the one options match the first one is selected
    :arg test_platform: For testing purposes, send in a tuple in the same format
                        as :func:`platform.system_alias()` 
    '''

    if test_platform: 
        system, release, version = test_platform
    else:
        system, release, version = this_platform = platform.system_alias(
                                                    platform.system(), 
                                                    platform.release(), 
                                                    platform.version())
    for option in options:
        match, select = option

        # Create a list of None for the ignored system specifiers  
        match_padding = [None] * (3 - len(match))

        match_system, match_release, match_version =\
                (match + match_padding)

        if match_system and not re.match(match_system, system):
            continue

        if match_release and not re.match(match_release, release):
            continue

        if match_version and not re.match(match_version, version):
            continue

        return select

    return None


old_modules = []
def dynload_module(modulename, modules, objects):
    ''' Replace module with a modules that loads objects dynamically 

    Here be dragons!

    Almost completly copied from Werkzeug

    '''
    global old_modules

    
    old_module = sys.modules[modulename]

    # Keep reference so it doesnt get garbage collected
    old_modules.append( old_module )

    # Try to get version from the module
    version = getattr(old_module, '__version__', '')

    modules = dict.fromkeys(modules)
  
    object_origins = {}
    for module, items in objects.iteritems():
        for item in items:
            object_origins[item] = module

    class dyn_module(ModuleType):
        def __getattr__(self, name):
            if name in object_origins:
                module = __import__(object_origins[name], None, None, [name])
                for extra_name in objects[module.__name__]:
                    setattr(self, extra_name, getattr(module, extra_name))
                return getattr(module, name)
            elif name in modules:
                __import__('.'.join((modulename, name)))
            return ModuleType.__getattribute__(self, name)

        def __dir__(self):
            """Just show what we want to show."""
            result = list(new_module.__all__)
            result.extend(('__file__', '__path__', '__doc__', '__all__',
                           '__docformat__', '__name__', '__path__',
                           '__package__', '__version__'))
            return result

        __version__ = version
 

    new_module = sys.modules[modulename] = dyn_module(modulename)
    new_module.__dict__.update({
        '__file__':         old_module.__file__,
        '__path__':         old_module.__path__,
        '__doc__':          old_module.__doc__,
        '__all__':          tuple(object_origins) + tuple(modules),
        '__docformat__':    'restructuredtext en'
    })
 

def platform_module(modulename, platforms, interface):
    ''' Get a dynload_module for modules that has platform implementations
    
    Imports __all__ from the platform that match the current one into the
    calling module. All supported platforms in the platform list are made 
    available.

    :arg platforms: See :func:`platform_select` 

    '''
    objects = {}

    platform_name = platform_select(platforms)
    if platform_name:
        platform_module_name = '.'.join((modulename, platform_name))
        objects = {platform_module_name: interface}

    modules = [p[1] for p in platforms]

    dynload_module(modulename, modules, objects) 





