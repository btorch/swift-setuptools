""" See COPYING for license information """

import swiftst.consts as sc
import swiftst.common.utils as utils
from fabric.api import *
from fabric.network import *

def common_setup(options):
    '''
    This function will perform some setups that are common among all
    systems
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get upgrade %s '
             % sc.apt_opts)
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')

        '''
        Install some general tools
        '''
        sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get install %s %s '
             % (sc.apt_opts, ' '.join(sc.general_tools)))


def do_swift_generic_setup():
    '''
    This function will only install some common
    swift packages such as swift, python-swift and swift client
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get install %s %s ' % (sc.apt_opts,
                                         ' '.join(sc.packages['generic'])))
        utils.place_on_hold(' '.join(sc.packages['generic']))


def swift_node_setup(node_type):
    '''
    This function will simply setup a swift node according with
    the node_type received. Once the packages are installed it
    will place them on hold to avoid any package upgrades
    using apt-get upgrade command.

    The final_touches call is just to make sure some directories
    and proper permissions are set correctly which will be used by swift
    '''
    if 'generic' in node_type:
        pkgs = ' '.join(sc.packages['generic'])
    else:
        pkgs = ' '.join(sc.packages['generic'] + sc.packages[node_type])

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get install %s %s ' % (sc.apt_opts, pkgs))
        utils.place_on_hold(pkgs.split(' '))
        utils.final_touches(node_type)


def swift_generic_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type)


def swift_proxy_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type)


def swift_storage_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type)


def swift_saio_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type)
