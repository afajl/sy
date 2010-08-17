from fabric.api import *
from fabric.decorators import hosts
from fabric.contrib.console import confirm
import sy1 as sy


def test():
    with settings(warn_only=True):
        result = local('nosetests -a "!host" tests', capture=False)
    if result.failed and not confirm('Tests failed, Continue anyway?'):
        abort('Aborting at user request')
 

def build_doc():
    ver = sy.__version__
    with cd('docs'):
        local('make html')
       
def create_readme():
    local('cp docs/intro.rst README.rst')

def upload_pypi():
    local('python setup.py bdist_egg release upload')

def package():
    test()
    local('cp docs/intro.rst README.rst')
    upload_pypi()
    
def doc():
    build_doc()

