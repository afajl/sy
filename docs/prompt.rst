===========================
Prompt user for information
===========================


Examples
========

A simple prompt
---------------
.. literalinclude:: _python/prompt_session.py


This would result in sessions like this::

    Do you want to add a mailserver? [y/n]: n
    I know you want one!

      Which mailserver do you want?
      1) sendmail
      2) postfix
      3) qmail

      Choice: first
      You must use numbers
      Choice: 1
        Do you really want to use sendmail? [y/N]: q
        Answer yes or no
        Do you really want to use sendmail? [y/N]: y
      How many mails are you expecting per hour?: a lot!
      Answer must be a integer
      How many mails are you expecting per hour?: 5
      Whats you domainname?: foo,com
      Enter a domain like foo.com
      Whats you domainname?: foo.com

    Ok, setting up sendmail on foo.com expecting 5 m/h


Question and their errorresponses can be indented which makes us
able to create nicer nested prompts.

       
sy.prompt content
=================

.. automodule:: sy.prompt
    :members:
