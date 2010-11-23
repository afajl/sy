"""
:synopsis: Working with network interfaces

.. moduleauthor: Paul Diaconescu <p@afajl.com>

"""

MIN_INTERFACE_SPEED = 100

import time
import re
import os

import sy
from sy._internal import _missing



class Interface(object):
    '''
    Represents a network interface. Attributes are:

    .. attribute:: name

        Name of the interface

    .. attribute:: ipaddress
        
        IP address of the interface

    .. attribute:: netmask
        
        Netmask of the interface

    .. attribute:: ether
        
        Ethernet address (MAC) of the interface
 
    .. attribute:: has_link
        
        True if dladm reports that the interface has link

    .. attribute:: is_physical
        
        Interface is not logical, ex hme0

    .. attribute:: is_logical
        
        Interface is not physical, ex hme0:1
 
    .. attribute:: is_configured
        
        Interface is plumbed and shows up in ifconfig -a

    .. attribute:: is_full_duplex
        
        Interface is running in full duplex

    .. attribute:: is_up
        
        Interface is UP

    .. attribute:: is_standby
        
        Interface is set as STANDBY in an IPMP group

    .. attribute:: is_failed
        
        Interface is FAILED in an IPMP group

    .. attribute:: is_inactive
        
        Interface is INACTIVE

    .. attribute:: is_dhcp
        
        Interface is configured by DHCP

    .. attribute:: speed
        
        Interface speed nr of MB reported by dladm

    .. attribute:: group
        
        IPMP group the interface belongs to

    .. attribute:: zone
        
        Zone the interface belongs to
 

    '''
    __slots__ = set([
        'name',
        'has_link',
        'is_physical',
        'is_logical',
        'is_configured',
        'is_full_duplex',
        'is_up',
        'is_standby',
        'is_failed',
        'is_inactive',
        'is_dhcp',
        'speed',
        'ipaddress',
        'netmask',
        'ether',
        'group',
        'zone',
    ])

    def __init__(self, **kwargs):
        for attr in self.__slots__:
            setattr(self, attr, kwargs.get(attr, None))
        bad_keys = set(kwargs.keys()).difference(self.__slots__)
        if bad_keys:
            raise AttributeError('Bad arguments passed to init: %s' % 
                                  ', '.join(bad_keys))
        
    def update(self, other):
        assert isinstance(other, Interface)
        for attr in self.__slots__:
            other_attr = getattr(other, attr, None)
            if other_attr is not None:
                setattr(self, attr, other_attr)

    def __repr__(self):
        ret = ['<Interface:\n']
        for attr in self.__slots__:
            ret.append( '  %s: %s\n' % (attr, str(getattr(self, attr, None))))
        ret.append('>')
        return ''.join(ret)

    __str__ = __repr__

# _______________________________
# physical interfaces
_dladm_rx = re.compile(r'''
        ^          (?P<ifname>\w+)           # name of the interface
        \s+
        link: \s   (?P<link>\w+)             # link status
        \s+
        speed: \s  (?P<speed>\d+) \s+ Mbps   # link speed
        \s+
        duplex: \s (?P<duplex>\w+)           # link duplex
        ''', re.X
    ) 
def _get_physical():
    interfaces = {}
    for line in sy.cmd.outlines('dladm show-dev'):
        match = _dladm_rx.search( line )
        if match:
            ifname = match.group('ifname')
            intf = Interface()
            intf.name = ifname
            intf.is_physical = True
            intf.has_link = match.group('link') == 'up'
            intf.speed = int( match.group('speed') )
            intf.is_full_duplex = match.group('duplex') == 'full'
            interfaces[ifname] = intf
    return interfaces


# _______________________________
# configured interfaces

_ifconfig_if_rx = re.compile(r'''
    ^(?P<ifname>[\w:]+):\s.*?           # interface name
    <(?P<flags>.*?)>                    # flags
    ''', re.X
    )
_ifconfig_ip_rx = re.compile(r'''
    \s inet \s (?P<ipaddress>[\d\.]+)      # ip address
     \s netmask \s (?P<netmask>\w+) \s   # netmask
                                        #  ! we ignore broadcast since
                                        #    it can be deduced
    ''', re.X
    )
_ifconfig_mac_rx = re.compile(r'''
    \s ether \s (?P<ether>[\w:]+)  # ether/mac address
    ''', re.X
    )
_ifconfig_group_rx = re.compile(r'''
    \s groupname \s (?P<group>\w+)     # IPMP group
    ''', re.X
    )
_ifconfig_zone_rx = re.compile(r'''
    \s zone \s (?P<zone>\w+) \s       # zone name
    ''', re.X
    )
 
def _get_configured():
    interfaces = {}
    intf = None
    for line in sy.cmd.outlines('ifconfig -a'):
        match = _ifconfig_if_rx.search(line)
        if match:
            if intf:
                interfaces[intf.name] = intf
            intf = Interface()
            intf.name = match.group('ifname')
            intf.is_configured = True

            if ':' in intf.name:
                intf.is_logical = True

            # set flags
            flags = set( match.group('flags').split(',') )
            intf.is_up       = 'UP'       in flags
            intf.is_standby  = 'STANDBY'  in flags
            intf.is_inactive = 'INACTIVE' in flags
            intf.is_failed   = 'FAILED'   in flags
            intf.is_dhcp     = 'DHCP'     in flags
            continue
        match = _ifconfig_ip_rx.search(line)
        if match:
            intf.ipaddress = match.group('ipaddress')
            mask = match.group('netmask')
            # step through hexmask (ffff0000) and create list of 
            # octets ['255','255' ...]  
            mask_bits = [int(a+b, 16) for a, b in zip(mask[0::2], mask[1::2])]
            intf.netmask = '.'.join([str(b) for b in mask_bits]) 
            continue
        match = _ifconfig_mac_rx.search(line)
        if match:
            intf.ether = match.group('ether')
            continue
        match = _ifconfig_group_rx.search(line)
        if match:
            intf.group = match.group('group')
            continue
        match = _ifconfig_zone_rx.search(line)
        if match:
            intf.zone = match.group('zone')
            continue
    if intf:
        interfaces[intf.name] = intf
    return interfaces
 

_interfaces_cache = {}
def _get_all():
    global _interfaces_cache
    if _interfaces_cache:
        return _interfaces_cache

    physical_intfs = _get_physical() 
    configured_intfs = _get_configured() 

    all_ifnames = set(physical_intfs.keys()) | set(configured_intfs.keys()) 

    for ifname in all_ifnames:
        # create a empty interface
        intf = Interface()

        # populate from physical data (dladm) if it exists
        physical_intf = physical_intfs.get(ifname)
        if physical_intf:
            intf.update(physical_intf)

        # populate from configured data (ifconfig) if it exists 
        configured_intf = configured_intfs.get(ifname)
        if configured_intf:
            intf.update(configured_intf)

        _interfaces_cache[ifname] = intf
    return _interfaces_cache

def _wait_for_status(ifname, timeout=10):
    waited = 0
    intf = get(ifname)
    while waited < timeout:
        if intf.speed != 0:
            return intf 
        intf = get(ifname)
        time.sleep(3)
        refresh()
        waited += 3
    return intf




# _______________________________________________________________________
# Public functions

def find(default=_missing, **kwargs):
    ''' Return all interfaces that matches the keyword arguments and values

    Keyword argument must match the attributes of the :class:`Interface`. Example::

        import sy

        sy.net.intf.find(ipaddress='10.0.0.1')
        ['<Interface: e1000g0>']

        sy.net.intf.find(is_logical=True, is_up=True)
        ['<Interface: e1000g0:1>', '<Interface: e1000g0:2>']


    :returns: List of :class:`Interface` matching keyword=values
    '''

    matched_interfaces = []
    for intf in _get_all().values():
        matches = 0
        # go through all key word arguments, like name=e1000g0 and 
        # match against interface
        for key, value in kwargs.items():
            intf_value = getattr(intf, key, _missing)  
            if intf_value is _missing:
                raise sy.Error('Key does not exists in "Interface": ' + key)
            if intf_value == value:
                matches += 1
        if matches == len(kwargs):
            matched_interfaces.append(intf)

    return matched_interfaces
                   
def get(ifname, default=_missing):
    ''' Return :class:`Interface` with the ifname 
    
    :arg default: What to return if the interface is missing.
    :returns: Matching :class:`Interface`
    :raises: :exc:`sy.Error` if the interface does not exist and ``default``
              is not supplied.

    '''
    intf = _get_all().get(ifname, None)
    if intf is None:
        # no interface found
        if default is not _missing:
            return default
        else:
            raise sy.Error('Interfaces %s does not exist' % ifname)
    return intf

def all():
    ''' Return a list of :class:`Interface` objects for every interface on the 
        server (even unconfigured) 

    '''
    return _get_all()

def refresh():
    ''' Clear the cache on interfaces. Useful if interfaces are changed by
    something else then this module.
    '''
    global _interfaces_cache
    sy.log.debug('Refreshing interface cache')
    _interfaces_cache = {}


#def get_physical_interface(ifname, cached_ok=False, wait=0):
    #intf = physical_interfaces().get(ifname)
    #if not intf:
        #raise sy.Error('Interface %s does not exist' % ifname)
    #if cached_ok:
        #return intf
    #if wait == 0:
        #return intf
    ## wait for status
    #waited = 0
    #while intf['speed'] == 0:
        #log('debug', 'Waiting for interface status for: %s', ifname)
        #if waited > wait:
            #raise sy.Error('Timeout waiting for status for %s' % ifname)
        #time.sleep(3)
        #waited += 3
        #intf = physical_interfaces()[ifname]
    #return intf

def check(ifname, ipaddress=None, netmask=None, group=None,
                    min_interface_speed=MIN_INTERFACE_SPEED):
    """ check if a interface is up and configured as specified

    :arg ipaddress: IP address in dotted decimal to check
    :arg netmask: Netmask in dotted decimal to check
    :arg group: Group that the interface should belong to 
    :arg min_interface_speed: minimum interface speed in (Mbit)
    :raises: :exc:`sy.Error` if the interface does not conform
    """ 
    intf = _wait_for_status(ifname)
    if not intf.is_up:
        raise sy.Error('Interface %s is not up' % ifname)
    if netmask and intf.netmask != netmask:
        raise sy.Error('Interface %s has the wrong netmask: %s' % 
                            (ifname, intf.netmask))
    if ipaddress and intf.ipaddress != ipaddress:
        raise sy.Error('Interface %s has the wrong IP address: %s' % (
                            ifname, intf.ipaddress))
    if group and intf.group != group:
        raise sy.Error('Interface %s has the wrong group: %s' % 
                            (ifname, intf.group))

    if intf.speed < min_interface_speed:
        raise sy.Error(
            'Interface %s speed is to low: %d' % (ifname, intf.speed))
    if not intf.is_full_duplex:
        raise sy.Error('Interface %s is not in full duplex' % ifname)

 
def unconfigure(ifname=None, ipaddress=None):
    """ Unconfigure a interface permanently

    You must supply one of the arguments 

    :arg ifname: interface name to unconfigure, i.e 'e1000g0'
    :arg ipaddress: IP address of interface to unconfigure 
    :returns : None or raises :exc:`CommandError` if unable to remove interface 
    """ 
    if ifname is not None:
        existing_intfs = [get(ifname)]
    elif ipaddress is not None:
        existing_intfs = find(ipaddress=ipaddress)
        if not existing_intfs:
            raise sy.Error('No interface found with IP "%s"' % ipaddress)
    else:
        raise sy.Error('You must specify ifname or ipaddress')

    for existing_intf in existing_intfs:
        if not existing_intf.is_configured:
            continue
        if existing_intf.is_logical:
            _unconfigure_logical(existing_intf)
        else:
            _unconfigure_physical(existing_intf)


def _unconfigure_physical(intf):
    ifname = intf.name

    sy.log.info('Unconfiguring interface %s' % ifname)
    try:
        sy.cmd.do('ifconfig {} unplumb', ifname,
                        prefix='Unable to unconfigure interface %s' % ifname)
    finally:
        refresh()

    hostname_path = '/etc/hostname.' + ifname
    if os.path.exists(hostname_path):
        os.unlink(hostname_path)

    dhcp_path = '/etc/dhcp.' + ifname
    if os.path.exists(dhcp_path):
        os.unlink(dhcp_path)

def _unconfigure_logical(intf):
    physical_ifname, _ = intf.name.split(':')  

    cmd =  ['ifconfig', physical_ifname, 'removeif', intf.ipaddress]
    try:
        sy.cmd.do('ifconfig {} removeif {}', 
                            physical_ifname, intf.ipaddress,
                            prefix='Unable to unconfigure logical interface %s' %
                                 intf.name)
    finally:
        refresh()

    hostname_path = '/etc/hostname.' + physical_ifname
    if os.path.exists(hostname_path):
        sy.path.remove_lines(hostname_path, '^addif ' + intf.ipaddress) 
    

def _check_network(ipaddress, netmask):
    if not sy.net.ip.is_valid(ipaddress):
        raise sy.Error('IP address is not valid: %s' % ipaddress)

    if not sy.net.ip.is_valid(netmask):
        raise sy.Error('Netmask is not valid: %s' % netmask)

    configured_intfs = find(ipaddress=ipaddress)
    if configured_intfs:
        raise sy.Error('IP address %s already configured on %s' % (
                        ipaddress, 
                       ','.join([i.name for i in configured_intfs])))
 
def _add_network(ipaddress, netmask):
    # add the network to netmasks
    network = sy.net.ip.get_network(ipaddress, netmask)
    sy.net.ip.add_netmask(network, netmask)
 

def configure(ifname, ipaddress=None, netmask=None, group=None, 
                      standby=False, hostname=None, permanent=True):
    ''' Configures a physical interface

    Configures the interface, add the netmask to netmasks, adds hostname
    to /etc/hosts and administers orgasms

    :arg ifname: Name of the interface to configure
    :arg ipaddress: IP address in dotted decimal to set
    :arg netmask: Netmask in dotted decimal to set
    :arg group: Group that the interface should belong to 
    :arg standby: The interface should be a standby IPMP interface
    :arg hostname: Hostname to set
    :arg permanent: If the interface should be configured on reboot
    :returns: None or raises exc:`CommandError` if unable to remove interface 
    '''
    

    sy.log.debug('Configuring interface %s' % ifname)

    if not get(ifname).is_physical:
        raise sy.Error('Interface %s does not exist' % ifname)

    unconfigure(ifname)

    cmd =  ['ifconfig', ifname, 'plumb']
    ifconfig = []
    if ipaddress:
        # Add network to /etc/inet/netmasks
        _check_network(ipaddress, netmask)
        _add_network(ipaddress, netmask)

        ifconfig.append(ipaddress)
        if netmask:
            ifconfig.extend(['netmask', netmask])
    if group:
        ifconfig.extend(['group', group])
        if ipaddress:
            ifconfig.append('deprecated')
        if standby:
            ifconfig.append('-failover')
    ifconfig.append('up')

    cmd = ' '.join(cmd + ifconfig)
    try:
        sy.cmd.do(cmd, prefix='Unable to configure interface %s'  % ifname)
    finally:
        refresh()
    try:
        check(ifname, ipaddress, netmask, group) 
        if permanent:
            if hostname:
                sy.net.ip.add_hostentry(ipaddress, hostname)
            # line to add to hostname.<interface>
            hostname_conf = ' '.join(ifconfig) + '\n'
            sy.path.dump('/etc/hostname.' + ifname, hostname_conf)
    except Exception, e:
        unconfigure(ifname)
        raise e


def addif(ifname, ipaddress, netmask, hostname=None, permanent=True):
    ''' Adds a logical interface

    Configures the interface on another, add the netmask to netmasks, 
    adds hostname to /etc/hosts

    :arg ifname: Name of the interface to add this on to
    :arg ipaddress: IP address in dotted decimal to set
    :arg netmask: Netmask in dotted decimal to set
    :arg hostname: Hostname to set
    :arg permanent: If the interface should be configured on reboot
    :returns: None or raises exc:`CommandError` if unable to remove interface 
    '''
    
 
    interfaces = all()


    physical_intf = get(ifname, None)
    if physical_intf is None:
        raise sy.Error('Physical interface, "%s", was not found' % ifname)
    if not physical_intf.is_configured:
        raise sy.Error('Physical interface, "%s", is not configured' % ifname)

    # Add network to /etc/inet/netmasks
    _check_network(ipaddress, netmask)
    _add_network(ipaddress, netmask)

    ifconfig = ['addif', ipaddress, 'netmask', netmask, 'up']
    cmd = ' '.join(['ifconfig', ifname] + ifconfig)
    try:
        sy.cmd.do(cmd, prefix='Unable to add IP %s'  % ifname)
    finally:
        refresh()

    if permanent:
        try:
            if hostname:
                sy.net.ip.add_hostentry(ipaddress, hostname)
            # line to add to hostname.<interface>
            hostname_conf = ' '.join(ifconfig) + '\n'
            sy.path.append('/etc/hostname.' + ifname, hostname_conf)
        except Exception, e:
            unconfigure(ipaddress=ipaddress)
            raise e



