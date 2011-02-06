=====================
Files and directories
=====================


This module contains functions for working with files and directories.
Check the standard modules :mod:`os.path` for more path functions. 


Examples
========
Writing files
-------------

Write string to a file
......................
:: 

    import sy.path

    # Write 'hello world' to /tmp/hello
    sy.path.dump('/tmp/hello', 'hello world\n')

    # Appending bye world' to the end of /tmp/hello
    sy.path.append('/tmp/hello', 'bye world\n')



Extract an archive
..................
:: 

    import sy.path

    # Extract /var/tmp/huge.tar.bz2 to /var/tmp 
    sy.path.extract('/var/tmp/huge.tar.bz2', '/var/tmp')



Reading files
-------------

Getting file content
....................
::

    import sy.path

    # Return content of file as a string
    sy.path.slurp('/tmp/hello')
    'hello world\nbye world\n'

    # Return lines from file
    sy.path.lines('/tmp/hello')
    ['hello world\n', 'bye world\n']

    # Return lines without newline character
    sy.path.lines('/tmp/hello', newline=False)
    ['hello world', 'bye world']


Checking content
................
::

    import sy.path

    # Check if file contains pattern
    sy.path.contains('/tmp/hello', 'hell.*world')
    True

    # Get the md5 sum of a file
    sy.path.md5sum('/etc/passwd')
    'dad86c61eea237932f201009e5431609'

    # Check if the content of two files are different
    sy.path.md5sum('/etc/passwd') == sy.path.md5sum('/etc/passwd.old')
    False


Replace content in text files
-----------------------------
These functions change the content on files in-place. They try to be as
safe as possible and should fail nicely without corrupting files.

::

    import sy.path

    # Remove all lines matching 'b.*world' from file
    sy.path.remove_lines('/tmp/hello', r'b.*world')
    1

    # Replace whole lines matching 'ello world' with 'alo world'
    sy.path.replace_lines('/tmp/hello', r'.*ello world', r'alo world')
    1

    # Switch places on 'alo' and 'world'
    sy.path.replace('/tmp/hello', r'(\w+) (\w+)', r'\2 \1')
    1


Path operations
---------------
::

    import sy.path

    # Clean up and expand paths
    sy.path.expandpath('$JAVA_HOME/bin')
    '/opt/java6/bin'
    sy.path.expandpath('~/.profile')
    '/export/home/john/.profile'
    sy.path.expandpath('/var/tmp/../adm')
    '/var/adm'

    # Make 'john' own '/tmp/hello'
    sy.path.chown('/tmp/hello', 'john')

    # Change group on '/tmp/hello' to 100
    sy.path.chown('/tmp/hello', None, 100)

    # Get the owner of '/tmp/hello'
    sy.path.owner('/tmp/hello')
    'john'

    # Get the group GID of '/tmp/hello'
    sy.path.group('/tmp/hello', gid=True)
    100

    # Return the permissions on '/tmp/hello'
    sy.path.mode('/tmp/hello')
    0644

    # Remove files, rm -rf style
    sy.path.rmtree('/tmp/junk')


sy.path content
===============

.. automodule:: sy.path
    :members:

    .. autofunction:: dump(path, content, binary=False, encoding=None, newline=os.linesep)




