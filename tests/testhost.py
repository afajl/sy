
hosts = {
    'solaris10u8': {
        'interfaces': ['e1000g1', 'e1000g2', 'e1000g3'],
        'test_ipmp': True,
    },
}

def get_info():
    import platform
    try:
        return hosts[platform.node()]
    except KeyError:
        raise RuntimeError(
            'This OS instance "%s" is not configured as a test host, ' % platform.node() 
            + 'run with "nosetest -a \'!host\' tests" or add this ' 
            + 'host to "%s"' % __file__)


