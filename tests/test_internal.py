from nose.tools import eq_
from sy._internal import platform_select

def test_platform_select():
    options = [
        (['Solaris', r'2.(9|10)'], 'solaris'),
    ]

    selection = platform_select(options, ('Solaris', '2.10', '')) 
    eq_(selection, 'solaris')

def test_platform_select_general():
    options = [
        (['Solaris', r'2.10'], 'solaris'),
        (['Solaris'], 'solarisgen'),
    ]

    selection = platform_select(options, ('Solaris', '2.9', '')) 
    eq_(selection, 'solarisgen')

def test_platform_select_general_bad_order():
    options = [
        (['Solaris'], 'solarisgen'),
        (['Solaris', r'2.10'], 'solaris'),
    ]

    selection = platform_select(options, ('Solaris', '2.10', '')) 
    eq_(selection, 'solarisgen')
 
