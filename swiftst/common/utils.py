""" See COPYING for license information """

import swiftst.consts as sc
from swiftst.exceptions import HostListError
from fabric.api import *
from fabric.network import *


def generate_hosts_list(dsh_group):
    '''
    Generates the list of hosts from a dsh group
    file and than feeds that list to the proper
    fabric roles
    '''
    dsh_path = '/etc/dsh/group/'
    dsh_file = dsh_path + dsh_group
    host_list = []
    try:
        if os.path.isfile(dsh_file):
            with open(dsh_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if not line.startswith('#'):
                            host_list.append(line)
        else:
            status = 404
            msg = "DSH file not found (%s)" % dsh_file
            raise HostListError(status, msg)
    except:
        status = 404
        msg = "Problem reading dsh file (%s)" % dsh_file
        raise HostListError(status, msg)

    if host_list:
        return host_list
    else:
        status = 204
        msg = "DSH group file has no content (%s)" % dsh_file
        raise HostListError(status, msg)


def add_keyrings():
    '''
    installs any keyring package that is available in the dict
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        sudo('apt-get install %s %s' % (sc.apt_opts, ' '.join(sc.keyrings)))


def setup_swiftuser():
    '''
    Setting up the user allows one to avoid issues when the UID
    could later on be changed from system setup to another due to
    some ubuntu changes as it has happened before with mlocate
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        check = run('id swift', quiet=True)
        if not check.succeeded:
            sudo('groupadd -g 400 swift')
            sudo('useradd -u 400 -g swift -G adm -M -s /bin/false swift')


def place_on_hold(pkg_list):
    '''
    Places the swift packages in maybe others in a hold status
    That prevents apt-get upgrade from trying to install new versions
    '''
    for name in pkg_list:
        sudo('echo "%s hold" | dpkg --set-selections' % name)


def final_touches(sys_type=''):
    check = run('test -d /var/cache/swift', quiet=True)
    if not check.succeeded:
        sudo('mkdir -p /var/cache/swift')
    check = run('test -d /etc/swift', quiet=True)
    if check.succeeded:
        sudo('chown -R swift.swift /etc/swift')
    sudo('chown swift.swift /var/cache/swift')

    if 'storage' in sys_type:
        check = run('test -d /srv/node', quiet=True)
        if not check.succeeded:
            sudo('mkdir -p /srv/node')
        check = run('test -d /var/log/swift/stats', quiet=True)
        if not check.succeeded:
            sudo('mkdir -p /var/log/swift/stats')
        sudo('chown swift.swift /var/log/swift/stats')


def check_installed(packages):
    '''
    This function will install an utility if not preset
    '''
    for name in packages:
        with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
            c = local('dpkg -s %s' % name, capture=True)
            if c.failed:
                local('apt-get install %s %s' % (sc.apt_opts, name))
    return True
