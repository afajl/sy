import sy.prompt

# Ask a yes or no question
yes = sy.prompt.confirm('Do you want to add a mailserver? [y/n]: ')

if not yes:
    print 'I know you want one!'
print

# Mailserver choices
mailservers = ['sendmail', 'postfix', 'qmail']

# Let the user choose a mailserver
selected = sy.prompt.choose('  Which mailserver do you want?', mailservers)
mailserver = mailservers[selected]

if mailserver == 'sendmail':
    usesendmail = sy.prompt.confirm(
                      '    Do you really want to use sendmail? [y/N]: ',
                      default=False)
    if not usesendmail:
        import sys
        sys.exit(0)

# Get a number
mailsperhour = sy.prompt.ask('  How many mails are you expecting per hour?: ',
                             type=int) 

# Check the response
domainname = sy.prompt.ask('  Whats you domainname?: ', checks=[
                            ('^\w+\.\w+$', 'Enter a domain like foo.com')])
print
print 'Ok, setting up', mailserver, 'on', domainname, 'expecting %d m/h' % mailsperhour

