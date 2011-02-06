This library is a set of easy to use modules to help with automation of 
system administration tasks::

  import sy.path, sy.net.intf, sy.net.ip, sy.cmd

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
 
  # Check if port 22 is answering on bart
  if not sy.net.ip.port_is_open('bart', 22):
     sy.log.warning('Ssh is down on bart') 
  


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
.. _git: http://git-scm.com

The repository path for ``sy`` is located at 
http://github.com/pauldiacon/sy. Clone with `git`_ by typing::

    $ git clone http://github.com/pauldiacon/sy.git

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

The documentation is built with `sphinx`_ and is locate under the ``docs`` folder.


