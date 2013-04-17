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
def add_keyrings():
    '''
    installs any keyring package that is available in the dict
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        sudo('apt-get install %s %s' % (sc.apt_opts, ' '.join(sc.keyrings)))


@parallel(pool_size=5)
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


def disk_setup(conf):
    '''
    This will setup the disks under /srv/node
    Don't like this it's a mess right now! Not in use!
    Also need to check on the cofig options before trying to
    setup anything here
    '''
    regex = re.compile(conf['device_pattern'])
    cmd1 = 'parted -s /dev/%s mklabel gpt'
    cmd2 = 'sz=$(parted -s /dev/%s print|grep "Disk"|cut -d ":" -f 2|tr -d " ");'
    cmd3 = 'parted -s /dev/%s mkpart primary xfs 0 $sz'
    cmd4 = 'mkfs.xfs -i size=1024 -d su=64k,sw=1 -f -L %s /dev/%s1'
    cmd5 = 'mkdir -p /srv/node/%s'
    cmd6 = 'LABEL=%s /srv/node/%s xfs defaults,noatime,nodiratime,nobarrier,logbufs=8  0  0'

    for controller in range(4):
        for num in range(conf['device_count']):
            dev = 'c' + controller + 'u' + num + 'p'
            label = 'c' + controller + 'u' + num

            '''
            The c0u0p should always be OS related
            device therefore skipped
            '''
            if dev == 'c0u0p':
                continue

            with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                          warn_only=True):
                if regex.match(dev):
                    if run('test -e /dev/%s1' % dev).succeeded:
                        status = 500
                        msg = 'Device already found with partition (%s)' % dev
                        raise DiskSetupError(status, msg)

                    if run('test -e /dev/%s' % dev).failed:
                        break

                    if run('test -e /dev/%s' % dev).succeeded:
                            sudo(cmd1 % dev)
                            sudo(cmd2 % dev + cmd3 % dev)
                            sudo(cmd4 % (label, dev))
                            sudo(cmd5 % label)
                        if run('grep "%s xfs" /etc/fstab' % label).failed:
                            cmd = cmd6 % (label, label)
                            sudo('echo %s >> /etc/fstab' % cmd)
