import codecs
import re
import os, os.path
import tempfile
from nose.tools import eq_, with_setup, assert_raises


import sy.path
import util


def teardown():
    util.tmppath.teardown()


# _______________________________________________________________________
# Encoding

given = (u'Hello world\n'
         u'\u0d0a\u0a0d\u0d15\u0a15\r\n'
         u'\u0d0a\u0a0d\u0d15\u0a15\x85'
         u'\u0d0a\u0a0d\u0d15\u0a15\u2028'
         u'\r'
         u'hanging') 
expected = (u'Hello world\n'
         u'\u0d0a\u0a0d\u0d15\u0a15\n'
         u'\u0d0a\u0a0d\u0d15\u0a15\n'
         u'\u0d0a\u0a0d\u0d15\u0a15\n'
         u'\n'
         u'hanging')   

expected_lines_retain = expected.splitlines(True)
expected_lines = expected.splitlines()



def test_encoding():
    ''' Test encoding '''
    p = util.tmppath()
    def test(enc):
        f = codecs.open(p, 'w', enc)
        f.write(given)
        f.close()

        eq_(sy.path.slurp(p, binary=True), given.encode(enc))
        eq_(sy.path.slurp(p, encoding=enc), expected)
        eq_(sy.path.lines(p, encoding=enc), expected_lines_retain) 
        eq_(sy.path.lines(p, encoding=enc, newline=False), expected_lines)

        expected_nohang = expected + u'\n'
        sy.path.dump(p, expected_nohang, encoding=enc)
        sy.path.append(p, expected_nohang, encoding=enc)

        # utf-16 writes BOM to the middle of the file on appending
        # dont test further
        if enc == 'utf-16':
            return

        expected_bytes = 2*expected_nohang.replace('\n', os.linesep).encode(enc)
        expected_lines_retain_nohang = expected_lines_retain[:]
        expected_lines_retain_nohang[-1] += '\n'
        eq_(sy.path.slurp(p, binary=True), expected_bytes) 
        eq_(sy.path.slurp(p, encoding=enc), 2*expected_nohang)
        eq_(sy.path.lines(p, encoding=enc), 2*expected_lines_retain_nohang)
        eq_(sy.path.lines(p, encoding=enc, newline=False), 2*expected_lines)

    test('utf8')
    test('utf-16be')
    test('utf-16le')
    test('utf-16')


# _______________________________________________________________________
# basic (no encoding stuff)

basic_given = (u'This line contains letters and some more\n'
               u'This line contains a num8er\n'
              )


def setup_basic():
    p = util.tmppath('basic')
    sy.path.dump(p, basic_given)


def test_open_read_bad_file():
    cmd = lambda: sy.path.slurp('/nonexistant')
    assert_raises(IOError, cmd)

    cmd = lambda: sy.path.slurp('')
    assert_raises(IOError, cmd)

def test_dump_newline():
    p = util.tmppath()
    sy.path.dump(p, '\r')
    eq_(sy.path.slurp(p), '\n')

    sy.path.dump(p, '\r\n', newline=None)
    eq_(sy.path.slurp(p), '\n')
 
    sy.path.dump(p, '\r', newline=None)
    eq_(sy.path.slurp(p, binary=True), '\r')

    sy.path.dump(p, '\r\n', newline=None)
    eq_(sy.path.slurp(p, binary=True), '\r\n')
 

@with_setup(setup_basic)
def test_contains_found():
    p = util.tmppath('basic')
    assert sy.path.contains(p, 'letters')
    assert sy.path.contains(p, '\d')
    assert sy.path.contains(p, 'num.er\n')
    assert not sy.path.contains(p, 'people')

@with_setup(setup_basic)
def test_md5sum():
    p = util.tmppath('basic')
    eq_(sy.path.md5sum(p), '5a0b7eaaa1b487776afd6e68eb9fbd29')
    eq_(sy.path.md5sum(p, hex=False), 'Z\x0b~\xaa\xa1\xb4\x87wj\xfdnh\xeb\x9f\xbd)')

    # compare with os command
    try:
        md5sum = sy.cmd.find('md5sum')
    except sy.CommandError:
        # not comparing to os md5sum
        print 'Not comparing to os md5sum'
        return
    out, _ = sy.cmd.do(md5sum + ' {}', p)
    ossum, _ = out.split()
    eq_(sy.path.md5sum(p), ossum)





 
# _______________________________________________________________________
# replace functions

replace_given = (u'first_line\n'
                 u'second_line column2\n'
                 u'third_line column2 column3\n')

replace_expect_line = (u'first_line_replaced\n'
                 u'second_line_replaced\n'
                 u'third_line_replaced\n')

replace_expect = (u'first_line\n'
                 u'second_line col2\n'
                 u'third_line col2 col3\n')

replace_expect_sub = (u'line_first\n'
                 u'line_second column2\n'
                 u'line_third column2 column3\n')
 
replace_expect_multiline = (u'first_line\n'
                 u'second_line x\n'
                 u'x\n')
 
def setup_replace():
    p = util.tmppath('replace')
    sy.path.dump(p, replace_given)
 
@with_setup(setup_replace)
def test_replace_line_keywords():
    p = util.tmppath('replace')
    nr = sy.path.replace_lines(p, matching='first_line', 
                             replacement='first_line_replaced') 
    eq_(nr, 1)
 

@with_setup(setup_replace)
def test_replace_line():
    p = util.tmppath('replace')
    sy.path.replace_lines(p, 'first_line', 'first_line_replaced') 
    sy.path.replace_lines(p, 'second_line', 'second_line_replaced') 
    sy.path.replace_lines(p, 'column3', 'third_line_replaced') 
    eq_(sy.path.slurp(p), replace_expect_line)


@with_setup(setup_replace)
def test_replace_remove_keywords():
    p = util.tmppath('replace')
    nr = sy.path.remove_lines(p, matching='irst_line') 
    eq_(nr, 1)
 

@with_setup(setup_replace)
def test_replace_remove():
    p = util.tmppath('replace')
    sy.path.remove_lines(p, 'irst_line') 
    eq_(len(sy.path.slurp(p).splitlines()), 2, msg='re.search should be used')
    sy.path.remove_lines(p, '.*column2$') 
    eq_(len(sy.path.slurp(p).splitlines()), 1)


@with_setup(setup_replace)
def test_replace_basic():
    p = util.tmppath('replace')
    nr = sy.path.replace(p, match='column', replacement='col')
    eq_(sy.path.slurp(p), replace_expect)
    eq_(nr, 3)

@with_setup(setup_replace)
def test_replace_multiline():
    p = util.tmppath('replace')
    rx = re.compile('column2.*', re.DOTALL)
    sy.path.replace(p, rx, 'x\nx\n')
    eq_(sy.path.slurp(p), replace_expect_multiline)
 
@with_setup(setup_replace)
def test_replace_sub():
    p = util.tmppath('replace')
    sy.path.replace(p, r'(\w+)_line', r'line_\1')
    eq_(sy.path.slurp(p), replace_expect_sub)

@with_setup(setup_replace)
def test_replace_sub_M():
    p = util.tmppath('replace')
    rx = re.compile('^(\w+)_line', re.MULTILINE)
    sy.path.replace(p, rx, r'line_\1')
    eq_(sy.path.slurp(p), replace_expect_sub)
 
 
@with_setup(setup_replace)
def test_replace_count_remove():
    p = util.tmppath('replace')
    nr = sy.path.remove_lines(p, matching='column') 
    eq_(nr, 2)

@with_setup(setup_replace)
def test_replace_count_replace_lines():
    p = util.tmppath('replace')
    nr = sy.path.replace_lines(p, matching='column', replacement='') 
    eq_(nr, 2)

@with_setup(setup_replace)
def test_replace_count_replace():
    p = util.tmppath('replace')
    nr = sy.path.replace(p, match='column2', replacement='c')
    eq_(nr, 2)
 
 

#@with_setup(setup_replace)
#def test_replace_inplace():
    #p = tempfiles[0]
    #rename_col_filter = lambda f: re.sub('column', 'col', f.read()) 
    #sy.path.replace_inplace(p, rename_col_filter)
    #eq_(sy.path.slurp(p), replace_expect_inplace)

#@with_setup(setup_replace)
#def test_replace_inplace():
    #p = tempfiles[0]
    #rx = re.compile('column2.*', re.DOTALL)
    #multiline_filter = lambda f: rx.sub('x\nx\n', f.read()) 
    #sy.path.replace_inplace(p, multiline_filter)
    #eq_(sy.path.slurp(p), replace_expect_inplace_multiline)
 


class TestExtract(object):
    def setup(self):
        self.archive_dir = util.in_data_dir('path_extract')
        self.tempdir = tempfile.mkdtemp(prefix='test_path', dir='/var/tmp')
        self.ok_file = os.path.join(self.tempdir, 'extract_test', 'ok')


    def teardown(self):
        sy.path.rmtree(self.tempdir)

    def _extract(self, archive):
        sy.path.extract(os.path.join(self.archive_dir, archive), 
                                         self.tempdir)
        assert os.path.exists( self.ok_file ) 
        eq_(sy.path.slurp( self.ok_file ), 'ok\n')

    def test_extract_tar(self): self._extract('ok.tar')
    def test_extract_zip(self): self._extract('ok.zip')
    def test_extract_tar_gz(self): self._extract('ok.tar.gz')
    def test_extract_tar_bz2(self): self._extract('ok.tar.bz2')
 





