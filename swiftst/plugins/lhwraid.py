""" See COPYING for license information """

import swiftst.consts as sc
from fabric.api import *
from fabric.network import *

'''
This module should provide functions to install available
packages that are provided by http://hwraid.le-vert.net for
ubuntu
'''

def add_repo():
    check = run('test -e /etc/apt/sources.list.d/megaraid.list', quiet=True)
    if check.failed:
        sudo('''
             echo "deb http://hwraid.le-vert.net/ubuntu precise main" >
             /etc/apt/sources.list.d/hwraid.le-vert.net.list
             ''')


def install_tools(tools):
    '''
    This function will install some tools for LSI
    '''
    add_repo()

    sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
    sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get install %s %s '
         % (sc.apt_opts, ' '.join(tools)))


def lsi_tools():
    '''
    This function will install some tools for LSI
    '''
    tools = ['megacli', 'megaclisas-status', 'sas2ircu', 'sas2ircu-status']
    install_tools(tools)


def tware_tools():
    '''
    This function will install some tools for 3Ware
    '''
    tools = ['tw-cli', '3ware-status', '3dm2']
    install_tools(tools)
