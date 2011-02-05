from nose.tools import assert_raises, eq_
import sy.cmd

echocmd = 'echo stdout; echo stderr > /dev/fd/2'

# _______________________________________________________________________
# format_cmd

def test_format_cmd_ok():
    s = sy.cmd.format_cmd('cmd {} {}', ['a', r''' '"$\t'''])
    eq_(s, '''cmd a \\ \\'\\"\\$\\t''')

def test_format_cmd_bad_nr_arguments():
    c = lambda: sy.cmd.format_cmd('cmd {} {}', ['a'])
    assert_raises(TypeError, c)

def test_format_escape():
    s = sy.cmd.format_cmd(r'find {} -exec ls \{\} \;', ('/tmp',))
    eq_(s, 'find /tmp -exec ls \\{\\} \\;')

 
# _______________________________________________________________________
# run function

def test_run_simple():
    returncode, out, err = sy.cmd.run('ls /etc/passwd')
    assert returncode == 0
    assert out == '/etc/passwd\n'
    assert err == ''

def test_run_format():
    returncode, out, err = sy.cmd.run('ls {} {} | sort', 
                                       '/etc/passwd', '/etc/hosts')
    assert returncode == 0
    assert out == '/etc/hosts\n/etc/passwd\n'
    assert err == ''


def test_run_relative_path():
    import os
    os.chdir('/bin')
    returncode, out, err = sy.cmd.run('./ls -d /tmp')
    assert returncode == 0
    assert out == '/tmp\n'
    assert err == ''

def test_run_env():
    import os
    envvar = 'SY_TEST_VAR'
    os.environ[envvar] = envvar
    returncode, out, err = sy.cmd.run('echo ${}', envvar)
    assert returncode == 0
    assert out == envvar + '\n'
    assert err == ''

def test_run_error():
    status, out, err = sy.cmd.run('%s; exit 3' % echocmd)
    eq_(status, 3)
    eq_(out, 'stdout\n')
    eq_(err, 'stderr\n')

def test_run_timeout_read():
    try: 
        returncode, out, err = sy.cmd.run('echo first; sleep 2; echo second',
                                      timeout=1)
        assert False, 'There should be a timeout'
    except sy.cmd.CommandTimeoutError, e:
        eq_(e.out, 'first\n')

def test_run_timeout():
    cmd = '%s; sleep 2' % echocmd
    try:
        sy.cmd.run(cmd, timeout=1) 
        assert False, 'There should be a timeout'
    except sy.cmd.CommandTimeoutError, e:
        eq_(str(e), 'Command "%s" timed out after 1 secs' % cmd) 
        eq_(e.out, 'stdout\n')
        eq_(e.err, 'stderr\n')
        eq_(e.timeout, 1)
        eq_(e.cmd, cmd)

def test_run_timeout_block():
    errcmd = lambda: sy.cmd.run('cat', timeout=1)
    assert_raises(sy.cmd.CommandTimeoutError, errcmd)
 
def test_run_no_cmd():
    try:
        status, out, err = sy.cmd.run('')
        assert False, 'No command should fail'
    except AssertionError, e:
        eq_(str(e), 'Missing command')

def test_run_bad_keyword():
    try:
        sy.cmd.run(echocmd, bad_keyword=0)
        assert False
    except AssertionError, e:
        eq_(str(e), 'Unknown keyword arg passed to run: bad_keyword')
 

# _______________________________________________________________________
# do function

def test_do_ok():
    out, err = sy.cmd.do(echocmd)
    eq_(out, 'stdout\n')
    eq_(err, 'stderr\n')

def test_do_fail():
    try:
        sy.cmd.do(echocmd, expect=1)
        assert False
    except sy.cmd.CommandError, e:
        eq_(str(e), 'Command "%s" did not exit with status 1: stderr' % echocmd)
        eq_(e.out, 'stdout\n')
        eq_(e.err, 'stderr\n')

def test_do_bad_keyword():
    try:
        sy.cmd.do(echocmd, bad_keyword=0)
        assert False
    except AssertionError, e:
        eq_(str(e), 'Unknown keyword arg passed to run: bad_keyword')

