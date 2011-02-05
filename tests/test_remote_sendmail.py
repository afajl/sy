from nose.tools import eq_, with_setup
import util


import smtplib
import sy.net
import sy.path

class TestSendmail(object):
    def __init__(self):
        self.original_SMTP = smtplib.SMTP
        self.smtp = None
        self.inbox = []
        self.msg = [('to', ['p@afajl.com']), 
                    ('subject', 'subject'), 
                    ('message', 'message'),
                    ('sender', 'foo@bar')]
        self.msg_dict = dict(self.msg)
        self.msg_args = (m[1] for m in self.msg)
 

    def setup(self):
        testobj = self
        class DummySMTP(object):
            def __init__(self, host=None, port=None, timeout=None):
                self.host = host
                self.port = port
                self.timeout = timeout
                testobj.smtp = self

            def connect(self, host, port):
                self.host = host
                self.port = port

            def sendmail(self, sender, to, message):
                testobj.inbox.append({
                    'sender': sender,
                    'to': to,
                    'message': message})
                return []

            def quit(self):
                self.has_quit = True

        # Monkeypatch
        smtplib.SMTP = DummySMTP

    def tear_down(self):
        smtplib.SMTP = self.original_SMTP
        self.smtp = None
        self.inbox = []
        util.tmppath.teardown()
     
    def _assert_message_eq(self, sent, got, mimeattach=''):
        eq_(sent['to'], got['to']) 
        eq_(sent['sender'], got['sender']) 

        mimemsg = ('Content-Type: multipart/mixed; '
                   'boundary="===============0820002584=="\n'
                   'MIME-Version: 1.0\n'
                   'To: %(to)s\n'
                   'Subject: subject\n'
                   'From: %(sender)s\n\n'
                   '%(message)s\n'
                   '--===============0820002584==\n'
                   'Content-Type: text/plain; charset="us-ascii"\n'
                   'MIME-Version: 1.0\n'
                   'Content-Transfer-Encoding: 7bit\n\n'
                   '%(message)s\n'
                   '--===============0820002584==--\n')
        fixed_sent = sent
        fixed_sent['to'] = ', '.join(sent['to'])
        mimemsg = mimemsg % fixed_sent
        mimemsg += mimeattach

        assert 'Subject: %s\n' % sent['subject'] in got['message']
        eq_(len(mimemsg), len(got['message']), 
            'Mime message does not match SENT:\n %s\n\nGOT:\n %s' % (
                mimemsg, got['message']))
 

    def test_keyword_args(self):
        sy.net.sendmail(**self.msg_dict)

        eq_(len(self.inbox), 1) 
        received = self.inbox[0]
        self._assert_message_eq(self.msg_dict, received)

    def test_positional_args(self):
        sy.net.sendmail(*self.msg_args)
        eq_(len(self.inbox), 1) 
        received = self.inbox[0]
        self._assert_message_eq(self.msg_dict, received)
 
    def test_unknown_attachment(self):
        p = util.tmppath()
        sy.path.dump(p, 'attachment')
        msg = {'attachments': [p]}
        msg.update(self.msg_dict)

        mimeattach = ('Content-Type: application/octet-stream\n'
                      'MIME-Version: 1.0\n'
                      'Content-Transfer-Encoding: base64\n'
                      'Content-Disposition: attachment;'
                      'filename="SY_TEST_Ozmxzu"\n\n'  
                      'YXR0YWNobWVudA==\n'
                      '--===============1919994729==--')

        sy.net.sendmail(**msg)
        eq_(len(self.inbox), 1) 
        self._assert_message_eq(self.msg_dict, self.inbox[0],
                                mimeattach=mimeattach)

    def test_txt_attachment(self):
        p = util.tmppath(suffix='.txt')
        sy.path.dump(p, 'attachment')
        msg = {'attachments': [p]}
        msg.update(self.msg_dict)

        mimeattach = ('Content-Type: text/plain; charset="us-ascii"\n'
                      'MIME-Version: 1.0\n'
                      'Content-Transfer-Encoding: 7bit\n'
                      'Content-Disposition: attachment;'
                      'filename="SY_TEST_Ozmxzu.txt"\n\n'  
                      'attachment\n'
                      '--===============1919994729==--')

        sy.net.sendmail(**msg)
        eq_(len(self.inbox), 1) 
        self._assert_message_eq(self.msg_dict, self.inbox[0],
                                mimeattach=mimeattach)
        
    def test_timeout(self):
        if not sy.net.ip.port_is_open('127.0.0.1', 25):
            return
        smtplib.SMTP = self.original_SMTP
        msg = {'mailhost': 'localhost',
               'mailport': 25, 
               'timeout': 0.001}
        msg.update(self.msg_dict)
 
        import socket
        try:
            sy.net.sendmail(**msg)
            assert False, 'Sendmail localhost should timeout'
        except socket.timeout:
            pass
 

    def test_bad_server(self):
        smtplib.SMTP = self.original_SMTP
        msg = {'mailhost': 'xxxxxx',
               'mailport': 66999, 
               'timeout': 0.1}
        msg.update(self.msg_dict)
 
        import socket
        try:
            sy.net.sendmail(**msg)
            assert False, 'Sendmail to bad server should fail'
        except socket.gaierror:
            pass


