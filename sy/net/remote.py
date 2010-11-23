'''
:synopsis: Utilities for working with servers on the network.

'''

import sy

import urllib
import os
import pwd
import platform
import os.path
import urllib2
import smtplib

import mimetypes

try:
    from email import Encoders
    from email.Message import Message
    from email.MIMEAudio import MIMEAudio
    from email.MIMEBase import MIMEBase
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEImage import MIMEImage
    from email.MIMEText import MIMEText
except ImportError:
    # Python 2.7
    from email import encoders as Encoders
    from email.message import Message
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText


def sendmail(to, subject, message, sender=None, attachments=(), 
             mailhost='localhost', mailport=25, timeout=60.0):
    ''' Send an email

    :arg to: List of recipients
    :arg subject: Subject of the message
    :arg message: Message body
    :arg sender: From address of the sender default to <current user>@<hostname>
    :arg attachments: List if paths to files you want to attach
    :arg mailhost: Mailserver to send through, default localhost
    :arg mailport: Mailserver port to send through, default 25
    :arg timeout: Timeout for sending the mail
    '''

    if isinstance(to, basestring):
        to = [to]

    if not sender:
        username = pwd.getpwuid(os.geteuid()).pw_name
        hostname = platform.node() 
        sender = '%s@%s' % (username, hostname)

    outer = MIMEMultipart()
    outer['To'] = ', '.join(to)
    outer['Subject'] = subject
    outer['From'] = sender
    outer.epilogue = ''

    if message:
        outer.preamble = message
        msg = MIMEText(message)
        outer.attach(msg)


    for attachment in attachments:
        if not os.path.isfile(attachment):
            sy.log.warn('Attachment is not a file: %s', attachment)
            continue

        ctype, encoding = mimetypes.guess_type(attachment)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)

        if maintype == 'text':
            msg = MIMEText(sy.path.slurp(attachment), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(sy.path.slurp(attachment, binary=True),
                            _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(sy.path.slurp(attachment, binary=True), 
                            _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(sy.path.slurp(attachment, binary=True))
            Encoders.encode_base64(msg)

        msg.add_header('Content-Disposition', 'attachment', 
                       filename=os.path.basename(attachment))
        outer.attach(msg)


    import socket
    defaulttimeout = socket.getdefaulttimeout()
    s = smtplib.SMTP()
    try:
        socket.setdefaulttimeout(timeout)
        s.connect(mailhost, mailport)
        s.sendmail(sender, to, outer.as_string())
    finally:
        socket.setdefaulttimeout(defaulttimeout)




def download(url, target):
    ''' Download a file through http or ftp '''

    url_f = urllib2.urlopen(url)
    target_f = None
    try:
        target_f = open(target, 'wb')
        for chunk in url_f:
            target_f.write(chunk)
    finally:
        url_f.close()
        if target_f:
            target_f.close()

