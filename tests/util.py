import tempfile
import os.path
import os
import urllib2
from StringIO import StringIO

test_dir = os.path.abspath(os.path.dirname(__file__))

in_data_dir = lambda p: os.path.join(test_dir, 'data', p)

class Temppath(object):
    def __init__(self):
        self.paths = {}

    def __call__(self, named=None, suffix=''):
        if named in self.paths:
            return self.paths[named]
        _, path = tempfile.mkstemp(suffix=suffix, prefix='SB_TEST_')
        key = named or path
        self.paths[key] = path
        return path

    def teardown(self):
        for path in self.paths.values():
            if os.path.exists(path):
                os.unlink(path)
        self.paths = {}


tmppath = Temppath()
        
class MockHTTPHandler(urllib2.HTTPHandler):
    def __init__(self, *args, **kwargs):
        self.mock_url = kwargs.pop('mock_url', None) 
        self.mock_file = kwargs.pop('mock_file', 'mock file') 
        self.mock_msg = kwargs.pop('mock_msg', 'mock msg') 
        self.mock_code = kwargs.pop('mock_code', 200) 
        self.mock_resp_msg = kwargs.pop('mock_resp_msg', 'OK') 
        self.resp_func = kwargs.pop('resp_func', None)

        urllib2.HTTPHandler.__init__(self, *args, **kwargs)

    def http_open(self, req):
        if self.resp_func:
            return resp_func(req)

        if self.mock_url and self.mock_url != req.get_full_url():
            resp = urllib2.addinfourl(StringIO('Not Found'), 'Not Found', 
                                      req.get_full_url()) 
            resp.code = 404
            resp.msg = 'Not Found'
            return resp

        resp = urllib2.addinfourl(StringIO(self.mock_file), self.mock_msg,
                                  req.get_full_url())
        resp.code = self.mock_code
        resp.msg = self.mock_resp_msg
        return resp

def setup_urllib_mock(mockopener):
    opener = urllib2.build_opener(mockopener)
    urllib2.install_opener(opener)

def teardown_urllib_mock():
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
 
