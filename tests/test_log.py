import os, os.path

import logging
from nose.tools import assert_raises, eq_
import sy
import util

class TestLogging(object):

    def tearDown(self):
        util.tmppath.teardown()
        rootlogger = logging.getLogger()
        rootlogger.handlers = []
        sy.log._quiet = False

    def test_logfile(self):
        debug_logfile = util.tmppath()
        warn_logfile = util.tmppath()
        sy.log.to_file(debug_logfile, level='debug')
        sy.log.to_file(warn_logfile, level='warning')

        sy.log.debug('log to debug')
        sy.log.info('log to debug')
        sy.log.warning('log to both')

        print open(debug_logfile).readlines()
        print open(warn_logfile).readlines()
        debug_lines = len(open(debug_logfile).readlines())
        warn_lines = len(open(warn_logfile).readlines())
        assert debug_lines == 3
        assert warn_lines == 1

    def test_log_name(self):
        import logging
        format = logging.Formatter('%(name)s')
        logfile = util.tmppath()
        sy.log.to_file(logfile, format=format)
        sy.log.error('foo')
        content = open(logfile).read().strip()
        eq_(content, 'tests.test_log')

    def test_badlevel(self):
        def test_level(level):
            sy.log.to_file('/tmp/foo', level=level)
            sy.log.to_syslog(level=level)
            sy.log.to_screen(level=level)

        test_level('debug')
        test_level('info')
        test_level('warning')
        test_level('warn')
        test_level('critical')
        test_level('error')

        assert_raises(AssertionError, sy.log.to_file, '/tmp/foo',
                      level='BADLEVEL')
        assert_raises(AssertionError, sy.log.to_syslog, level='BADLEVEL')
        assert_raises(AssertionError, sy.log.to_screen, level='BADLEVEL')


