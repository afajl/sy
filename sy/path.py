"""

:synopsis: Simplify operations on files and directories

.. moduleauthor: Paul Diaconescu <p@afajl.com>
"""


import os
import re
import grp, pwd
import codecs
import fcntl
import tempfile
import os.path
import stat
import sys
import shutil
import tarfile
import zipfile

import sy.log
import sy.cmd

log = sy.log._new('sy.path')
 

try:
    from hashlib import md5
except ImportError:
    import md5
    md5 = md5.new

import sy

from sy._internal import _missing

# _______________________________
# write files

def dump(path, content, append=False, binary=False, encoding=None, 
         newline=os.linesep):
    ''' Dump content to a file.

    Writes content to file, overwriting if the file exists. 
    Use :func:`append` to add to the of the file.

    :arg binary: Write binary data to the file
    :arg encoding: If content is unicode, specifies how it should be encoded 
                     in the file. Raises an assertion error if specified for
                     non-unicode content
    :arg newline: Convert all newlines types (Windows or Mac) to this. Default ``\\n`` on Unix.
                  If set to None, the content is written without changing any newlines. 

    '''

    if not binary:
        if isinstance(content, unicode):
            if newline is not None:
                # Convert all standard end-of-line sequences to
                # ordinary newline characters.
                content = (content.replace(u'\r\n', u'\n')
                                .replace(u'\r\x85', u'\n')
                                .replace(u'\r', u'\n')
                                .replace(u'\x85', u'\n')
                                .replace(u'\u2028', u'\n'))
                content = content.replace(u'\n', newline)       
            if encoding is None:
                encoding = sys.getdefaultencoding()
            bytes = content.encode(encoding, 'strict')
        else:
            assert encoding is None
            if newline is not None:
                content = (content.replace('\r\n', '\n')
                            .replace('\r', '\n'))
                bytes = content.replace('\n', newline)  
            else:
                bytes = content
    if hasattr(path, 'write'):
        # got an open filehandle
        fh = path
    else:
        if append:
            openmode = 'ab'
        else: 
            openmode = 'wb'
        fh = open(path, openmode)
 
    try:
        fh.write(bytes)
    finally:
        fh.close()

def append(*args, **kwargs):
    ''' Append content to file. Same arguments as to :func:`dump` ''' 
    kwargs['append'] = True
    dump(*args, **kwargs)

        
def extract(archive, dir):
    ''' Unpack a tar or zip file to the specified directory.

    Tarfiles compressed with gzip, bzip2 or compress are uncompressed.

    :arg archive: Path to the archive
    :arg dir: Directory where the archive will be uncompressed
    '''
    if not os.path.exists(archive):
        raise RuntimeError('Archive cannot be found at %s' % archive)

    # we can not use the extract functions from the tarfile and zipfile
    # modules since it is not supported on python 2.4
    if tarfile.is_tarfile(archive):
        archive_file = os.path.basename(archive)
        decompressor_table = {
            'gzcat': ('gz', 'tgz'),
            'bzcat': ('bz', 'bz2', 'tbz', 'tbz2'),
            'zcat' : ('tar.z', 'tz', 'tar.Z'),
        }

        streamer = 'cat'
        for cmd, file_endings in decompressor_table.items():
            for file_ending in file_endings:
                if archive_file.endswith(file_ending):
                    streamer = cmd
        sy.cmd.do('{} {} | (cd {}; tar xf -)', streamer, archive, dir)
    elif zipfile.is_zipfile(archive):
        sy.cmd.do('unzip {} -d {}', archive, dir)

 
# _______________________________
# read files

def _open_read(path, encoding=None, binary=False):
    if binary or encoding is None:
        if binary:
            mode = 'rb'
        else:
            mode = 'rU' # convert '\r\n' and '\r' to \n
        return open(path, mode)
    else:
        # Encoded
        return codecs.open(path, 'r', encoding, 'strict')


def slurp(path, encoding=None, binary=False):
    ''' Return a file as a string 
    
    :arg path: Path to file
    :arg encoding: The encoding of the file. 
                   Default is None which returns the file as a 8-bit string
                   which works well for latin1 and asci. 
    :arg binary: Treat the file as a binary, no conversions will be made
    '''
    f = _open_read(path, encoding=encoding, binary=binary)
    try:
        c = f.read()
    finally:
        f.close()
    if encoding:
        # unicode
        return (c.replace(u'\r\n', u'\n')
                 .replace(u'\r\x85', u'\n')
                 .replace(u'\r', u'\n')
                 .replace(u'\x85', u'\n')
                 .replace(u'\u2028', u'\n'))
    else:
        # binary or 8-bit text (opened with 'U' which converts newlines)
        return c


def lines(path, encoding=None, newline=True):
    ''' Return list of lines from file. 
    
    :arg newline: If true, keep newline characters for every line. 
                 Default is True.  All newline characters (``\\r``, ``\\r\\n``) 
                 are replaced by ``\\n``. 
    Same arguments as to :func:`slurp` 
    '''

    return slurp(path, encoding=encoding).splitlines(newline) 


def contains(path, pattern, encoding=None):
    ''' Returns True if the file contains a line that matches the string or 
        compiled pattern.

        :arg path: Path to the file
        :arg pattern: String or compiled pattern 
    '''
    if not hasattr(pattern, 'search'):
        pattern = re.compile(pattern)
    f = _open_read(path, encoding=encoding)
    try:
        for line in f:
            if pattern.search(line):
                return True
    finally:
        f.close()
    return False



def md5sum(path, hex=True):
    ''' Calculate md5 sum for a file.

    :arg hex: Return the digest in hexadecimal suitable for writing to 
                text files. Default True.
    '''
    f = open(path, 'rb')
    try:
        m = md5()
        while True:
            d = f.read(8192)
            if not d:
                break
            m.update(d)
    finally:
        f.close()
    if hex:
        return m.hexdigest()
    else:
        return m.digest()





# _______________________________
# replace content in file

def remove_lines(path, matching, encoding=None):
    ''' Remove lines from the ``path`` that matches ``matching``

        .. note:: 
            The line will match if the pattern is anywhere on the line. 
            See :func:`re.search` in the standard library.
 
        :arg path: Path to the file
        :arg matching: String to search for (or compiled regular expression)
        :returns: Number of lines removed
    '''
    if not hasattr(matching, 'search'):
        matching = re.compile(matching)

    def filter(original_f, new_f):
        nr_removed = 0
        for line in original_f:
            if matching.search(line):
                nr_removed += 1
                continue
            new_f.write(line)
        return nr_removed

    return _replace_file(path, filter, encoding=encoding)

def replace_lines(path, matching, replacement, encoding=None):
    ''' Replace lines that contain the string ``matching`` with ``replacement``

        .. note:: 
            The line will match if the pattern is anywhere on the line. 
            See :func:`re.search` in the standard library.

        :arg path: Path to the file
        :arg matching: String or compiled regular expression.
        :arg replacement: Line to replace with, newline character will 
            automatically be added if missing.
        :returns: Number of lines replaced
    '''
    if not hasattr(matching, 'search'):
        matching = re.compile(matching)

    if not replacement.endswith('\n'):
        replacement += '\n'

    def filter(original_f, new_f):
        nr_replaced = 0
        for line in original_f:
            if matching.search(line):
                new_f.write(replacement)
                nr_replaced += 1
            else:
                new_f.write(line)
        return nr_replaced

    return _replace_file(path, filter, encoding=encoding)


def replace(path, match, replacement, encoding=None):
    ''' Replace all occurances of ``match`` with ``replacement``. 
    Using :func:`re.sub`, backreferences in the replacement will work as
    normal::

        # change login of all users to 'leif'
        rx = re.compile(r'^\w+:(.*)', re.MULTILINE)
        replace('/etc/passwd', rx, r'leif:\\1') 

    .. note:: 
        Make sure your replacement uses a raw string (``r''``) if it contains 
        backreferences.


    :arg path: Path to the file
    :arg match: String to match
    :arg replacement: String to replace match with
    :returns: Number of replacements made
    '''
    if not hasattr(match, 'sub'):
        match = re.compile(match, re.MULTILINE)

    def filter(original_f, new_f):
        sub, nr_subs = match.subn(replacement, original_f.read())
        new_f.write(sub)
        return nr_subs
    return _replace_file(path, filter, encoding=encoding)
 


def _replace_file(path, filter_func, encoding=None):
    ''' This builder function replaces the content of the path
    with the output of the filter. The filter is passed the original file as 
    file object. Example usage::

        def filter(original_file, new_file):
            # replace all lines starting with XXX with YYY
            nr_replacements = 0
            for line in original_file: 
                if line.startswith('XXX'):
                    new_file.write.write('YYY\n')
                    nr_replacements += 1
                else:
                    new_file.write.write(line)
            return nr_replacements

        _replace_file(/etc/hosts', filter)

    Anything returned from the `filter_func` will be returned by this function

    See :func:`replace_lines` for an example
    '''

    # expand path and get target of eventual symlink
    path = os.path.realpath( expandpath(path) )

    # open and lock original file
    if encoding:
        original_file = codes.open(path, 'r+', encoding, 'strict')
    else:
        original_file = open(path, 'r+')
    fcntl.lockf(original_file.fileno(), fcntl.LOCK_EX)

    # get a temp file in the same directory as original file
    _, tmppath = tempfile.mkstemp(dir=os.path.dirname(path), 
                                      prefix=os.path.basename(path),
                                      suffix='.replacement')
    try:
        tmp_file = open(tmppath, 'wb')
        filter_ret = filter_func(original_file, tmp_file)
        tmp_file.close()
    finally:
        if not tmp_file.closed:
            tmp_file.close()
        original_file.close()

    try:
        # stat the original file so we can copy permissions
        pathst = os.stat(path)
        os.chmod(tmppath, pathst.st_mode)
        chown(tmppath, owner=pathst.st_uid, group=pathst.st_gid)
     
        # this should be an atomic operation on sane filesystems
        os.rename(tmppath, path)
    finally:
        if os.path.exists(tmppath):
            os.remove(tmppath)
    return filter_ret
  


 
# _______________________________
# path operations

def expandpath(path):
    ''' Clean up path.
    Expands environment vars like $JAVA_HOME, does tilde expansion for paths 
    like "~/.bashrc" and normalizes the path
    '''
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))

    

def chown(path, owner, group):
    ''' Change owner and group of a file or directory.

    If owner or group is None it is left unchanged. If both are set to None
    this function does nothing.

    If you use username or groupname that user or group must exist on the
    current system.

    :arg owner: Uid or username of the new owner. 
    :arg group: Gid or groupname of the new owner. 
    '''
    

    if owner is None:
        uid = -1    # dont modify
    elif isinstance(owner, int):
        uid = owner
    else: 
        # convert username to uid
        uid = pwd.getpwnam(owner).pw_uid

    if group is None:
        gid = -1    # dont modify
    if isinstance(group, int):
        gid = group
    else: 
        # convert group name to gid
        gid = grp.getgrnam(group).gr_gid

    log.debug('Chowning "{}" to uid={} and gid={}', path, uid, gid)
    os.chown(path, uid, gid)

def owner(path, uid=False):
    ''' Return username that owns the file or directory.

    :arg uid: If True return the uid as an integer
    '''
    st = os.lstat(path)
    uid = st.st_uid
    if uid:
        return uid
    return pwd.getpwuid(uid).pw_name

def group(path, gid=False):
    ''' Return the name of the group that owns the file or directory.

    :arg gid: If True return the gid as an integer
    '''
    st = os.lstat(path)
    gid = st.st_gid
    if gid:
        return gid
    return grp.getgrgid(gid).gr_name
    
def mode(path):
    ''' Permission mode of the file or directory.

    :returns: octal representation of the mode, ie 0644
    '''
    st = os.lstat(path)
    return oct(stat.S_IMODE(st.st_mode))
    

def rmtree(path, force=False):
    ''' Removes a directory and everything below it.

    :arg force: Ignores all errors, like rm -rf
    '''
    try:
        shutil.rmtree(path)
    except:
        if not force:
            raise

#def directory_tail(path, files='*', dirs='', method='timestamp'):
    #pass
