'''
:synopsis: Utilities for working with ip addressing and hosts

.. moduleauthor:: Paul Diaconescu <p@afajl.com>
'''
import socket

import sy
import ipaddr

def is_valid(ipaddress):
    ''' Checks if a IP address is valid '''
    try:
        ipaddr.IPAddress(ipaddress)
        return True
    except ValueError:
        return False

def get_network(ipaddress, netmask):
    ''' Returns the network address given an ipaddress and netmask'''
    return str(ipaddr.IPNetwork('%s/%s' % (ipaddress, netmask)).network)

def can_ping(host):
    ''' Test if host or ipaddress is pingable '''
    returncode, _, _ = sy.cmd.run('ping {}', host)
    if returncode != 0:
        return False
    else:
        return True

def port_is_open(ipaddress, port, timeout=1):
    ''' Check if a port is reachable and open 

    :arg ipaddress: IP address to the host
    :arg port: Port number
    :arg timeout: Number of seconds to wait for a connection
    :returns: True if the port is open, False otherwise
    '''
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((ipaddress, port))
        return True
    except:
        return False


def _hostfile_dict():
    hosts = {}
    for line in sy.path.lines('/etc/hosts'):
        if line.startswith('#'):
            continue
        hostentry = line.split()
        if len(hostentry) < 2:
            continue
        ipaddress = hostentry[0]
        hostnames = hostentry[1:]
        if not is_valid(ipaddress):
            sy.log.error('Bad IP found in /etc/hosts: %s', ipaddress)
            continue
        hosts[ipaddress]= hostnames
    return hosts
 

def add_hostentry(ipaddress, hostname, append_hostname=False):
    ''' Add a hostname to /etc/hosts

    :param ipaddress: IP of the host
    :param hostname: Hostname (and aliases)
    :param append_hostname: Append the hostnames if an entry for 
                            the IP already exists
    '''
    hostfile = _hostfile_dict()
    append_to_hosts = True
    if ipaddress in hostfile:
        if append_hostname:
            hostnames = set(hostfile[ipaddress] + [hostname])
        else:
            hostnames = [hostname]
        append_to_hosts = False
    else:
        hostnames = [hostname]

    new_line = '%s\t%s\n' % (ipaddress, ' '.join(hostnames))
    if append_to_hosts:
        sy.path.append('/etc/hosts', new_line)
    else:
        sy.path.replace_lines('/etc/hosts', ('^%s.*' % ipaddress), new_line) 


def _netmask_dict():
    netmasks = {}
    for line in sy.path.lines('/etc/inet/netmasks'):
        if line.startswith('#'):
            continue
        netmask = line.split()
        if len(netmask) < 2:
            continue
        netmasks[netmask[0]] = netmask[1]
    return netmasks
 

def add_netmask(network, netmask):
    ''' Add a netmask to /etc/inet/netmask

    Overwrites any old netmask with the same network IP
    '''                                  
    netmasks = _netmask_dict()
    line = '%s\t%s\n' % (network, netmask)
    if network in netmasks:
        sy.path.replace_lines('/etc/inet/netmasks', '^' + network, line)
    else:
        sy.path.append('/etc/inet/netmasks', line)


def set_nodename(name):
    sy.cmd.do('/bin/hostname {}', name, prefix='Unable to set hostname')
    sy.path.dump('/etc/nodename', name + '\n')


#def remove_hostname(ipaddress, hostname
 
#def ipnetwork_is_valid(ipaddress, netmask):
    #""" Checks if a ipnetwork is valid
    #:param ipaddress: IP address in dotted decimal or format accepted
                      #by `netaddr.IPAddress`
    #:param netmask:   netmask dotted decimal form (255.255.0.0) or bitmask (24) 
                      #or format accpeted by `netaddr.IPNetwork`
    #:returns: True if valid ip network, false otherwise
    #"""
    #try:
        #netaddr.IPNetwork(ipaddress + '/' + netmask)
        #return True
    #except AddrFormatError:
        #return False


#def on_same_network(ipnetworks):
    #""" Check if two ip addresses are on the same network
    #:param ipnetworks: iterable of dicts with keys 'ipaddress'and 'ipmask'
    #:returns: True if on the same network, false otherwise
    #"""

    #prev_network = None
    #for ipnetwork in ipnetworks:

        #assert 'ipaddress'in ipnetwork and 'ipmask' in ipnetwork, \
                #'ipnetwork must have keys ipaddress and ipmask'

        #this_network = netaddr.IPNetwork(
                        #'{ipaddress}/{ipmask}'.format(**ipnetwork)
                       #)

        #if prev_network is not None:
            #if prev_network != this_network:
                #return False

        #prev_network = this_network

    #return True
 
