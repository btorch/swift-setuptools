""" See COPYING for license information """

import swiftst.consts as sc
from swiftst.exceptions import HostListError, ConfigSyncError, DiskSetupError
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


@parallel(pool_size=5)
def add_keyrings(remote=True):
    '''
    installs any keyring package that is available in the dict
    '''
    cmds = ['apt-get update -qq -o Acquire::http::No-Cache=True ',
            'apt-get install %s %s ' % (sc.apt_opts, ' '.join(sc.keyrings))]

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        for cmd in cmds:
            if remote:
                sudo(cmd)
            else:
                local(cmd)


@parallel(pool_size=5)
def setup_swiftuser(remote=True):
    '''
    Setting up the user allows one to avoid issues when the UID
    could later on be changed from system setup to another due to
    some ubuntu changes as it has happened before with mlocate
    '''
    cmds = ['groupadd -g 400 swift',
            'useradd -u 400 -g swift -G adm -M -s /bin/false swift']

    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        if remote:
            check = run('id swift', quiet=True)
            if not check.succeeded:
                for cmd in cmds:
                    sudo(cmd)
        else:
            check = local('id swift')
            if not check.succeeded:
                for cmd in cmds:
                    local(cmd)


def place_on_hold(pkg_list, remote=True):
    '''
    Places the swift packages in maybe others in a hold status
    That prevents apt-get upgrade from trying to install new versions
    '''
    for name in pkg_list:
        cmd = 'echo "%s hold" | dpkg --set-selections' % name
        if remote:
            sudo(cmd)
        else:
            local(cmd)


def final_touches(sys_type='', remote=True):
    '''
    Creates some directories and update ownerships
    This functions really shouldn't be needed and this
    should be part of the packaging post install
    '''
    cmds = ['mkdir -p /var/cache/swift',
            'chown swift.swift /var/cache/swift',
            'mkdir -p /var/log/swift/stats',
            'chown swift.swift /var/log/swift/stats',
            'chown -R swift.swift /etc/swift']

    if remote:
        for cmd in cmds:
            sudo(cmd)
        if 'storage' in sys_type:
            sudo('mkdir -p /srv/node')
        if 'saio' in sys_type:
            sudo('mkdir -p /srv/node')

    else:
        for cmd in cmds:
            local(cmd)
        if 'storage' in sys_type:
            local('mkdir -p /srv/node')
        if 'saio' in sys_type:
            local('mkdir -p /srv/node')


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


def svn_setup(conf):
    '''
    Setting up SVN repo
    - create /srv/svn if not there yet
    - Make sure it has src as the group owner and 2777 perms 
    - add user(s) to the src group
    - make sure inetd.conf is present openbsd-inetd
    - echo "svn stream tcp nowait nast /usr/bin/svnserve svnserve -i -r /srv/svn" into inetd.conf and restart
    - svnadmin create /srv/svn/swift-cluster-configs
    - svn import SRC_DIR file:///srv/svn/swift-cluster-configs -m "Initial import"
    - change perms on /srv/svn for 
    '''


@parallel(pool_size=5)
def pull_configs(sys_type, conf):
    '''
    This function will git clone the repo on the admin box
    and then sync it over to the root
    '''
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        if run('test -d /root/local').succeeded:
            sudo('mv /root/local /root/local.old')

    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        loc_dir = '/root/local/' + sys_type
        sudo('git clone git://%s/%s /root/local' % (conf['admin_ip'],
                                                    conf['repository_name']))
        c = run('test -d %s' % loc_dir)
        if c.failed:
            status = 404
            msg = 'Directory was not found! (%s)' % loc_dir
            raise ConfigSyncError(status, msg)
        sudo('rsync -aq0c --exclude=".git" --exclude=".ignore" %s/ /'
              % loc_dir)
