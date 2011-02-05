from nose.tools import eq_, with_setup, assert_raises
import util
import urllib2

import sy.net

def teardown():
    util.tmppath.teardown()
    util.teardown_urllib_mock()

def test_http_download():
    mock = util.MockHTTPHandler()
    util.setup_urllib_mock(mock)
    p = util.tmppath()

    sy.net.download('http://www', p)

    eq_(sy.path.slurp(p), 'mock file')

def test_bad_target():
    mock = util.MockHTTPHandler()
    util.setup_urllib_mock(mock)

    try:
        sy.net.download('http://www', '/tmp')
        assert False, 'Specifying a dir should fail'
    except IOError:
        pass


def test_bad_url():
    def urlerror(req):
        raise urllib2.URLError('no host given')

    mock = util.MockHTTPHandler(resp_func=urlerror)
    util.setup_urllib_mock(mock)
    p = util.tmppath()

    try:
        sy.net.download('http:/www', p)
        assert False, 'Bad url should fail'
    except urllib2.URLError:
        pass

 
def test_nonexistant_url():
    mock = util.MockHTTPHandler(mock_url = 'http://xxx')
    util.setup_urllib_mock(mock)
    p = util.tmppath()

    try:                              
        sy.net.download('http://www', p)
        assert False, 'Download bad url should fail'
    except urllib2.HTTPError:
        pass

 










