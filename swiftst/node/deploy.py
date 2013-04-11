""" See COPYING for license information """

import os
import swiftst.consts as sc
import swiftst.common.utils as utils
from fabric.api import *
from fabric.network import *
from swiftst.exceptions import ResponseError 


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


@task
def adminbox_setup(conf):
    '''
    Setups up the admin box
    '''
    pkgs = ['rsync', 'dsh', 'git', 'git-core', 'nginx', 'subversion',
            'exim4', 'git-daemon-sysvinit', 'syslog-ng',
            'snmpd', 'snmp']
    
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        local('apt-get install %s %s' % (sc.apt_opts, ' '.join(pkgs)))

    '''
    Create and initialize repository    
    '''    
    name = 'swift-acct' + conf['account_number'] + '-' + conf['account_nick']
    src_loc = conf['genconfigs'] + '/' + name
    dst_loc = conf['repository_base'] + '/' + conf['repository_name']

    if not os.path.exists(src_loc):
        status = 500
        msg = 'Source directory does not exit (%s)' % src_loc
        raise ResponseError(status, msg)
    
    if not os.path.exists(conf['repository_base']):
        try:
            os.mkdir(conf['repository_base'])
        except Exception as e:
            (status, msg) = e.args
            raise ResponseError(status, msg)

    if os.path.exists(dst_loc):
        status = 500
        msg = 'Repository destination already seems to exist (%s)' % dst_loc
        raise ResponseError(status, msg)

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):     
        c = local('rsync -aq0c %s/ %s' % (src_loc, dst_loc))
        if c.failed:
            status = 500
            msg = 'Rsync of %s to %s has failed' % (src_loc, dst_loc)
            raise ResponseError(status, msg)

        try:
            'This sucks really wanted to use a python git api'
            pwd = os.getcwd()
            local('git init -q %s' % dst_loc)
            os.chdir(dst_loc)
            local('git add .')
            local('git commit -q -m "initial commit" -a')
            os.chdir(pwd)
        except Exception as e:
            if len(e.args) < 2:
                status = 500
                msg = e.args
            else:
                (status, msg) = e.args
            raise ResponseError(status, msg)

        '''
        Now sync the admin configs over to the system itself
        and then restart services like git-daemon and nginx
        '''
        if os.path.exists(dst_loc + '/admin'):
            c = local('rsync -aq0c --exclude=".git" --exclude=".ignore" %s/ /'
                      % (dst_loc + '/admin'))
            if c.failed:
                status = 500
                msg = 'Error syncing admin files from repo to /'
                raise ResponseError(status, msg)
        
        c = local('service git-daemon restart')
        if c.failed:
            status = 500
            msg = 'Error restarting git-daemon'
            raise ResponseError(status, msg)
                
        c = local('service nginx restart')
        if c.failed:
            status = 500
            msg = 'Error restarting nginx'
            raise ResponseError(status, msg)

    return True
