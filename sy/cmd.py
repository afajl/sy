'''
:synopsis: Running system commands
   
    

.. moduleauthor: Paul Diaconescu <p@afajl.com>
''' 
import time
import os
import select
import signal
import re

import sy.log
import sy.util

log = sy.log._new('sy.cmd')


CMD_TIMEOUT=60


class CommandError(Exception):
    ''' Command failed error 
    
    .. attribute:: out

       The stdout collected from the command

    .. attribute:: err

       The stdout collected from the command

    .. attribute:: status
            
       The commands exit status

    .. attribute:: cmd

        The command that was run
    '''
    def __init__(self, msg, out=None, err=None, status=None, cmd=None):
        self.out = out
        self.err = err
        self.status = status
        self.cmd = cmd
        Exception.__init__(self, msg)

class CommandTimeoutError(CommandError):
    ''' Command failed due to time out. Subclass of :exc:`CommandError`.
    
    .. attribute:: timeout

       The timeout that was exceeded

    '''
 
    def __init__(self, msg, timeout=None, *args, **kwargs):
        self.timeout = timeout
        CommandError.__init__(self, msg, *args, **kwargs)

 

class _subprocess(object):
    ''' Class representing a subprocess. Example usage:

        >>> proc = _subprocess('ls')
        >>> timed_out = proc.read(timeout=10)
        >>> return_code = proc.cleanup()
        >>> print proc.outdata, proc.errdata
        >>> del(proc)
    '''

    def __init__(self, cmd, bufsize=8192):
        self.cleaned = False
        self.BUFSIZE = bufsize
        self.outr, self.outw = os.pipe()
        self.errr, self.errw = os.pipe()
        self.pid = os.fork()
        if self.pid == 0:
            self._child(cmd)
        # parent doesnt write, so close
        os.close(self.outw)
        os.close(self.errw)

        self.outdata = self.errdata = ''
        self._outeof = self._erreof = 0

    def _child(self, cmd):
        os.setpgrp() # seperate group so we can kill it
        os.dup2(self.outw, 1) # stdout to write side of pipe
        os.dup2(self.errw, 2) # stderr to write side of pipe

        # stdout & stderr connected to pipe, so close all other files
        map(os.close, (self.outr, self.outw, self.errr, self.errw))
        try:
            cmd = ['/bin/sh', '-c', cmd]
            os.execvp(cmd[0], cmd)
        finally:
            os._exit(1)

    def read(self, timeout=None):
        currtime = time.time()
        while True:
            tocheck = []
            if not self._outeof:
                tocheck.append(self.outr)
            if not self._erreof:
                tocheck.append(self.errr)
            ready = select.select(tocheck,[],[],timeout)
            # no data timeout
            if len(ready[0]) == 0:
                return 1
            else:
                if self.outr in ready[0]:
                    outchunk = os.read(self.outr, self.BUFSIZE)
                    if not outchunk:
                        self._outeof = 1
                    self.outdata += outchunk
                if self.errr in ready[0]:
                    errchunk = os.read(self.errr, self.BUFSIZE)
                    if not errchunk:
                        self._erreof = 1
                    self.errdata += errchunk
                if self._outeof and self._erreof:
                    return 0
                elif timeout:
                    if (time.time() - currtime) > timeout:
                        return 1
    def kill(self):
        os.kill(-self.pid, signal.SIGTERM) # kill whole group

    def cleanup(self):
        self.cleaned = True
        os.close(self.outr)
        os.close(self.errr)
        pid, sts = os.waitpid(self.pid, 0)
        if pid == self.pid:
            self.sts = sts
        return self.sts

    def __del__(self):
        if not self.cleaned:
            self.cleanup()

_find_search_path = []

@sy.util.memoize
def find(cmd_name):
    ''' Search for the command and return the full path

    >>> import sy
    >>> sy.cmd.find('ifconfig')
    '/usr/sbin/ifconfig'

    Searches the directories specifiend in the environment PATH and a
    couple of default directories.

    :param cmd_name: Command to search for.
    ''' 
    global _find_search_path
    if not _find_search_path:
        import glob, platform
        # build the search path
        _find_search_path = os.environ.get('PATH', '').split(':')
        default_path = [
                '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/usr/local/bin', 
                '/usr/local/sbin'] + glob.glob('/opt/*/bin') 
        if platform.system() == 'SunOS':
            default_path.extend([
                '/usr/sfw/bin', '/usr/xpg4/bin', '/usr/xpg5/bin', 
                '/usr/java/bin', '/usr/ccs/bin',
                ])
        for path in default_path:
            if path not in _find_search_path:
                _find_search_path.append(path)

    for path in _find_search_path:
        cmd_path = os.path.join(path, cmd_name)
        if os.access(cmd_path, os.X_OK):
            return cmd_path
    raise CommandError('Command %s not found in path: %s' % (
        cmd_name, ':'.join(_find_search_path)))
 
def shell_escape(str):
    ''' Return the string with all unsafe shell character repaced '''
    return re.sub(r'''([ \t'"\$])''', r'\\\1', str)  

def format_cmd(command, args):
    r'''Format a shell command using safe escapes and argument substitutions::

        >>> format_cmd('ls -l {} | grep {} | wc', ['foo 1', 'bar$baz'])
        'ls -l foo\\ 1 | grep bar\\$baz | wc'

    Usually you don't need to call this, it is used to format the command
    by :func:`run`, and derived :func:`outlines` and :func:`do`

    .. note:: 

        You must escape ``{}`` in commands or pass it as a argument. These 
        have the same result::

            format_cmd('find . -exec ls \{\} \;')
            format_cmd('find . -exec ls {} \;', ['{}'])


    Taken from iterpipes
    '''

    if command.count('{}') != len(args):
        raise TypeError(
            'Number of arguments do not match the format string %r: %r' %
             (command, args))
    fmt = command.replace('%', '%%').replace('{}', '%s')
    return fmt % tuple(map(shell_escape, args)) 


def outlines(command, *args, **kwargs):
    ''' Spawn a command and return stdout lines. 
    Same arguments as :func:`do` expects
    :returns: stdout as list of lines
    '''
    out, _ = do(command, *args, **kwargs)
    return out.splitlines()
 

def do(command, *args, **kwargs):
    r'''Spawn a command and returns stdout and stderr. If the command
    does not exit with the ``expect`` status (default 0) it raises 
    :exc:`CommandError`.

    See :func:`run` for the other options.

    :arg expect: Expected exit status, default 0 
    :returns: stdout and stderr as strings
    '''
    expect = kwargs.pop('expect', 0)

    status, out, err = run(command, *args, **kwargs)

    if status != expect:
        escapedcmd = format_cmd(command, args)
        msg = 'Command "%s" did not exit with status %d: %s' % (
                escapedcmd, expect, err.strip()) 
        raise CommandError(msg, out=out, err=err, status=status, cmd=escapedcmd)
    return out, err
    


def run(command, *args, **kwargs):
    ''' Execute a command with a timeout and capture output and exit status::

            status, out, err = sy.cmd.run('ls -R {}', '/tmp', timeout=15) 
        
        Use the convenience function :func:`do` if you want to fire off a
        command and fail if it doesnt return exit status 0.                        
        
        :arg command: Command template
        :arg args: Arguments for formatting the command, see :func:`format_cmd`
        :arg timeout: Seconds until the command times out and raises 
                      a :exc:`CommandTimeoutError`
        :returns: exit status from the command, stdout and stderr. 
                  On timeout it raises :exc:`CommandTimeoutError`
    '''
    assert command, 'Missing command'
 
    timeout = kwargs.pop('timeout', CMD_TIMEOUT)
    bufsize = kwargs.pop('bufsize', 8192)
    assert kwargs == {}, 'Unknown keyword arg passed to run: ' + ','.join(kwargs.keys())
    
    escapedcmd = format_cmd(command, args)
    log.debug('Spawning: {}', escapedcmd)

    start_time = time.time()
    process = _subprocess(escapedcmd, bufsize=bufsize)
    if process.read(timeout):
        # process timed out
        process.kill()
        process.cleanup()
        errormsg = 'Command "%s" timed out after %d secs' % (escapedcmd, timeout)
        log.error(errormsg)
        raise CommandTimeoutError(errormsg, out=process.outdata, 
                                     err=process.errdata, cmd=escapedcmd, 
                                     timeout=timeout)

    exitstatus = os.WEXITSTATUS( process.cleanup() )
    out = process.outdata
    err = process.errdata
    del(process)

    log.debug('Command result, stdout:{}, stderr:{}, exitstatus:{}', 
                 out.strip(), err.strip(), exitstatus)
    log.debug('Command took {} seconds', int(time.time() - start_time))
    return exitstatus, out, err
