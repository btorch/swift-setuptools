""" See COPYING for license information """

import os
import swiftst.consts as sc
import swiftst.common.utils as utils
from fabric.api import *
from fabric.network import *
from swiftst.exceptions import ResponseError


@parallel(pool_size=5)
def common_setup(remote=True):
    '''
    This function will perform some setups that are common among all
    systems
    '''
    cmds = ['apt-get update -qq -o Acquire::http::No-Cache=True ',
            'export DEBIAN_FRONTEND=noninteractive; apt-get upgrade %s '
            % sc.apt_opts,
            'apt-get update -qq -o Acquire::http::No-Cache=True ',
            'export DEBIAN_FRONTEND=noninteractive ; apt-get install %s %s '
            % (sc.apt_opts, ' '.join(sc.general_tools))]

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        for cmd in cmds:
            if remote:
                sudo(cmd)
            else:
                local(cmd)


def swift_node_setup(node_type, remote=True):
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

    cmds = ['apt-get update -qq -o Acquire::http::No-Cache=True',
            'apt-get install %s %s ' % (sc.apt_opts, pkgs)]

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        if remote:
            for cmd in cmds:
                sudo(cmd)
            utils.place_on_hold(pkgs.split(' '))
            utils.final_touches(node_type)
        else:
            for cmd in cmds:
                local(cmd)
            utils.place_on_hold(pkgs.split(' '), False)
            utils.final_touches(node_type, False)


@parallel(pool_size=5)
def swift_generic_setup(node_type, remote=True):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type, remote)


@parallel(pool_size=5)
def swift_proxy_setup(node_type, remote=True):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type, remote)


@parallel(pool_size=5)
def swift_storage_setup(node_type, remote=True):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type, remote)


@parallel(pool_size=5)
def swift_saio_setup(node_type, remote=True):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        swift_node_setup(node_type, remote)


@task
@serial
def adminbox_setup(conf):
    '''
    This function will install some needed packages for the admin box
    also with some of the swift generic and common packages as well.
    Then it will take care of setting up the repository where the configs
    will be held.
    '''
    pkgs = ['rsync', 'dsh', 'git', 'git-core', 'nginx', 'subversion',
            'exim4', 'git-daemon-sysvinit', 'syslog-ng',
            'snmpd', 'snmp']

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        local('apt-get update -qq -o Acquire::http::No-Cache=True')
        local('apt-get install %s %s ' % (sc.apt_opts, ' '.join(pkgs)))

    '''
    Create and initialize repository
    '''
    print "[local] : Creating and Initializing repository"

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
        print "[local] : Syncing admin configs to system /"
        if os.path.exists(dst_loc + '/admin'):
            c = local('rsync -aq0c --exclude=".git" --exclude=".ignore" %s/ /'
                      % (dst_loc + '/admin'))
            if c.failed:
                status = 500
                msg = 'Error syncing admin files from repo to /'
                raise ResponseError(status, msg)

        print "[local] : Starting up git-daemon"
        c = local('service git-daemon restart')
        if c.failed:
            status = 500
            msg = 'Error restarting git-daemon'
            raise ResponseError(status, msg)

        print "[local] : Starting up nginx"
        c = local('service nginx restart')
        if c.failed:
            status = 500
            msg = 'Error restarting nginx'
            raise ResponseError(status, msg)

    '''
    Start setting up the box now. The False param indicates that
    the fabric local call should be used instead of the default
    remote call sudo
    '''
    print "[local] : calling add_keyrings"
    utils.add_keyrings(False)
    print "[local] : calling setup_swiftuser"
    utils.setup_swiftuser(False)
    print "[local] : calling common_setup"
    common_setup(False)
    print "[local] : calling swift_generic_setup"
    swift_generic_setup(['generic'], False)

    return True
