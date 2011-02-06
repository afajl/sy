==========
Networking
==========


Sending email
=============
::

    import sy.net

    sy.net.sendmail(to=['unix@foo.com', 'me@foo.com'],
                       subject='Script output',
                       message='The script did ...',
                       attachments=['/var/log/script.log'])
    


.. autofunction:: sy.net.sendmail


Downloading files
=================
:: 

    import sy.net

    # Downloads file from http server
    sy.net.download('http://server/file.tgz', '/var/tmp/myfile.tgz')
 
    # Downloads file from ftp server
    sy.net.download('ftp://server/file.tgz', '/var/tmp/myfile.tgz')

.. warning::
    Proxy settings from the environment will be used. To be sure
    that no proxy is configured remove the variable before download::

        import os
        del os.environ['http_proxy']
        del os.environ['ftp_proxy']


See the standard library :py:mod:`urllib2` module for more advanced
scenarios.

.. autofunction:: sy.net.download

.. automodule:: sy.net


IP tools - sy.net.ip
====================

.. automodule:: sy.net.ip
   :members:
 

Interfaces - sy.net.intf
========================

.. warning::
    These are only (slightly) tested and only works on Solaris 10 
 
.. automodule:: sy.net.intf
   :members:


