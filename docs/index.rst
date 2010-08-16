===
sy1
===

.. toctree::
   :maxdepth: 2

   path
   cmd
   prompt
   utilities
   net
 

Introduction
============
This library is a set of easy to use modules to help with automation of 
system administration tasks. To use the library import the version you want as 
``sy`` in your script::

  # Import the library
  import sy1 as sy

  # Replace lines in '/etc/hosts' that match nis.*
  sy.path.replace_lines('/etc/hosts', 'nis.*', '10.2.3.1 ldap')
  1

  # Fetch information about the interface hme0
  hme0 = sy.net.intf.get('hme0')

  # Get the IP of hme0
  hme0.ipaddress
  '192.168.2.2'

  # Check if hme0 is up
  hme0.is_up
  True

  # Find files named '*.pl' but time out after 10 seconds
  out, err = sy.cmd.do('find /mnt -name {}', '*.pl', timeout=10)

  # Setup a rotating log file that wont fill the disk
  sy.log.to_file('/var/tmp/app.log')
  
  # Check if port 22 is answering on bart
  if not sy.net.ip.port_is_open('bart', 22):
     sy.log.warning('Ssh is down on bart') 
  

Changes in the ``sy1`` library is guaranteed to *not* break your code. 
When incompatible changes are introduced new version will be installed as 
``sy2``, ``sy3`` and so on.

The library is heavily inspired by `Werkzeug`_ which is a great WSGI utility 
collection.

.. _Werkzeug: http://werkzeug.pocoo.org/

Developing
==========

.. _pip: http://pip.openplans.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _fabric: http://docs.fabfile.org/0.9.1/
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/
.. _sphinx: http://sphinx.pocoo.org/
.. _mercurial: http://mercurial.selenic.com/

The repository path for ``sy`` is located at 
http://bitbucket.org/pauldiacon/sy. Clone with `mercurial`_ by typing::

    $ hg clone http://zscmp01/hg/proj/dia/sbpy

The requirements for developing are listed in ``dev-reqs.pip`` that
can be install with `pip`_ with:: 

    $ pip install -r dev-reqs.pip

The library currently targets python 2.4.4 - 2.6.

Testing
-------

To run the test suite use `nose`_::

    $ nosetests -a '!host' tests

The ``!host`` parameter tells the suite to not run tests that change the hosts
configuration (like reconfiguring network interfaces).

There currently isn't any automated way to run the testsuite on virtual machines.
This feature is greatly needed to be able to test all parts of the library and
to test it on different versions and operating systems.


Documentation
-------------

The documentation is built with `sphinx`_ and is locate under the ``doc`` folder.




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

