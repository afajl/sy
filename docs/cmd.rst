================
Running commands
================

This module contains functions for running system commands. The difference
between this module and the standard :mod:`subprocess` is that it is easy
to use and all functions support setting a timeout.


Examples
========

Run a command with a timeout
----------------------------
::

  import sy

  status, out, err = sy.cmd.run('find / -name {}', '*.pl', timeout=90)
  print out
  
All commands take a command template, with ``{}`` indicating a placeholder, and
arguments for substitution. In the example above the command will become:
``find / -name \*.pl``. Note that the ``\*`` has been escaped properly. 
For more information see :func:`sy.cmd.format_cmd` and :func:`sy.cmd.run`.


Fail if exit status is not ok
-----------------------------
::
  
  import sy

  out, err = sy.cmd.do('ifconfig xxge0 up', 
                        prefix='Could not take up interface')
   
  # Will fail with sy.CommandError:
  #   Could not take up interface:\ 
  #     Command "ifconfig XXX up" did not exit with status 0:\
  #     ifconfig: interface XXX does not exist

The function :func:`sy.cmd.do` takes the same arguments as :func:`sy.cmd.run` but
only returns stdout and stderr and raises an exception if command did not exit
successfully.

This is convenient since this pattern of programming is encouraged::

  def main():
      sy.cmd.do('this')
      sy.cmd.do('that')
      sy.cmd.do('and that')

  try:
      main()
  except Exception, e:
      sy.log.exception('Script failed')
      sy.util.fail('Script failed: ' + str(e))

This way we now that if any command fails the execution will stop and
the error will be logged before exiting.


Loop through stdout
-------------------
To loop through the stdout lines of a command you can use :func:`sy.cmd.outlines`
which takes the same arguments as :func:`sy.cmd.do`::

  import sy

  # print the IP of the default route

  for mount in sy.cmd.outlines('mount', timeout=5):

      if 'nfs' in mount:
          print 'Found NFS mount:', mount.strip()


If the systems has any dangling NFS mounts the command would hang and an 
:exc:`sy.CommandTimeoutError` would be raised.  The exceptions :exc:`sy.CommandError` 
and its subclass :exc:`sy.CommandTimeoutError` contains all the information about 
why the command failed:: 

    try:
       sy.cmd.do('cat /etc/shadow')
    except sy.CommandError, e:
        # Descriptive message of the error
       str(e) == 'Command "cat /etc/shadow" did not exit with status 0, ...'

       # Stderr from the command
       e.err  == 'cat: /etc/shadow: Permission denied\n'
    
       # Stdout from the command
       e.out  == ''

       # Exit status of the command 
       e.status == 1

       # The command that was run
       e.cmd == 'cat /etc/shadow'
 
 
sy.cmd content
==============

.. automodule:: sy.cmd

  .. autofunction:: run(command, *args, timeout=CMD_TIMEOUT)

  .. autofunction:: do(command, *args, expect=0, prefix='', timeout=CMD_TIMEOUT)

  .. autofunction:: outlines(command, *args, expect=0, prefix='', timeout=CMD_TIMEOUT)

  .. autofunction:: find(command_name) 

  .. autofunction:: format_cmd(command, args)

