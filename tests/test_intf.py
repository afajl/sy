from nose.tools import assert_raises

import sy

import testhost

class TestIntf(object):
    host = True

    def setUp(self):
        self.host = testhost.get_info()
        for ifname in self.host['interfaces']:
            sy.net.intf.unconfigure(ifname)
 
    def tearDown(self):
        pass

    def test_get(self):
        for ifname in self.host['interfaces']:
            intf = sy.net.intf.get(ifname)
            assert intf.name == ifname 
            assert not intf.is_configured, 'Interfaces should not be configured'

        # non existant
        non_existant = lambda: sy.net.intf.get('blah')
        assert_raises(sy.Error, non_existant)

        # default value
        assert sy.net.intf.get('blah', default=42) == 42

    def test_all(self):
        all = sy.net.intf.all()
        for ifname in self.host['interfaces']:
            assert ifname in all

    def test_configure(self):
        ifname = self.host['interfaces'][0]
        sy.net.intf.configure(ifname, 
                              ipaddress = '99.99.99.99',
                              netmask = '255.255.255.0')
        intf = sy.net.intf.get(ifname)
        assert intf.ipaddress == '99.99.99.99'
        assert intf.netmask == '255.255.255.0'
        assert intf.is_up
        assert intf.is_configured
        assert intf.is_physical
        assert not intf.is_logical
        assert not intf.is_standby
        assert not intf.is_failed
        assert not intf.is_inactive
        assert intf.speed != 0
        assert intf.ether is not None
        assert not intf.group
        assert not intf.zone



    def test_bad_net(self):
        ifname = self.host['interfaces'][0]
        bad_ip = lambda: sy.net.intf.configure(ifname, '256.0.0.0') 
        bad_mask = lambda: sy.net.intf.configure(ifname, '256.0.0.0', 
                                                 netmask='259.255.255.0') 
        assert_raises(sy.Error, bad_ip) 
        assert_raises(sy.Error, bad_mask) 


    def test_logical(self):
        physical_ifname = self.host['interfaces'][0]

        ipaddress = '98.98.98.98'
        def add_logical():
            sy.net.intf.addif(physical_ifname, ipaddress, '255.255.255.0')
        assert_raises(sy.Error, add_logical)

        sy.net.intf.configure(physical_ifname)
        add_logical()

        found_logical = sy.net.intf.find(ipaddress=ipaddress)
        assert len(found_logical) == 1

        logical_intf = found_logical[0]
        assert logical_intf.ipaddress == ipaddress










