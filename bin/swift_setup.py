#!/usr/bin/env python

import os
import sys
import time
from optparse import OptionParser
from fabric.api import *
from fabric.network import *

# Set some ENVs
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'en_US.UTF-8'

# APT-GET Options
apt_opts = ' -y -qq --force-yes -o Dpkg::Options::=--force-confdef '
#apt_opts = ' -s --force-yes '

# Possible keyrings being used
_keyrings = ['ubuntu-cloud-keyring']

# Packages lists
generic_pkgs = ['swift', 'python-swift', 'python-swiftclient']
proxy_pkgs = ['swift-proxy']
storage_pkgs = ['swift-account', 'swift-container', 'swift-object']
other_pkgs = ['python-suds', 'python-slogging']

# Package dict
packages = {'generic': ['swift', 'python-swift', 'python-swiftclient'],
            'proxy': ['swift-proxy'],
            'storage': ['swift-account', 'swift-container', 'swift-object'],
            'saio': ['swift-proxy', 'swift-account', 'swift-container', 'swift-object'],
            'other': ['python-suds', 'python-slogging']
            }


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
    except:
        print "Error: problems reading dsh file %s " % dsh_file
        sys.exit(1)

    if host_list:
        return host_list
    else:
        print "Error: hosts list is empty "
        sys.exit(1)


def add_keyrings():
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        sudo('apt-get install %s %s' % (apt_opts, ' '.join(_keyrings)))


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


def setup_dell_tools():
    tools = ['megacli', 'megaclisas-status',
             'sas2ircu', 'srvadmin-all']
    sudo('gpg --list-keys >/dev/null')
    sudo('''
         gpg --keyserver pool.sks-keyservers.net
         --recv-key 1285491434D8786F
        ''')
    sudo('gpg -a --export 1285491434D8786F | apt-key add -')
    sudo('apt-get install %s %s ' % (apt_opts, ' '.join(tools)))
    sudo('/etc/init.d/dataeng restart')
    time.sleep(30)
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=NodeInterleave setting=Disabled
        ''')
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=ProcVirtualization setting=Disabled
        ''')
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=SysProfile setting=PerfOptimized
        ''')


def do_common_setup(options):
    '''
    This function will perform some setups that are common among all
    systems
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get upgrade %s '
             % apt_opts)
        sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
        '''
        if desired we would setup some system users here
        '''
        '''
        Install some general tools
        '''
        general_tools = ['python-software-properties', 'patch', 'debconf',
                         'bonnie++', 'dstat', 'python-configobj', 'curl',
                         'subversion', 'git-core', 'iptraf', 'htop',
                         'nmon', 'strace', 'iotop', 'debsums']
        sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get install %s %s '
             % (apt_opts, ' '.join(general_tools)))

        '''
        Here we need to add a call to a function to retrieve the
        config file from git in the admin box and then sync them over
        to the system root. Not yet implemented
        '''

        if options.platform:
            if 'dell' in options.platform:
                setup_dell_tools()


def do_swift_generic_setup():
    '''
    This function will only install some common
    swift packages such as swift, python-swift and swift client
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get install %s %s ' % (apt_opts, ' '.join(generic_pkgs)))
        place_on_hold(generic_pkgs)


def do_swift_node_setup(node_type):
    '''
    This function will simply setup a swift node according with
    the node_type received. Once the packages are installed it
    will place them on hold to avoid any package upgrades
    using apt-get upgrade command.

    The final_touches call is just to make sure some directories
    and proper permissions are set correctly which will be used by swift
    '''
    pkgs = ' '.join(packages['generic'] + packages[node_type])
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        sudo('apt-get install %s %s ' % (apt_opts, pkgs))
        place_on_hold(pkgs.split(' '))
        final_touches(node_type)


def do_swift_proxy_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        do_swift_node_setup(node_type)


def do_swift_storage_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        do_swift_node_setup(node_type)


def do_swift_saio_setup(node_type):
    '''
    Really just a wrapper function identify task
    '''
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        do_swift_node_setup(node_type)


def main():
    '''
    Main function
    '''
    parser = OptionParser(add_help_option=False)
    parser.add_option("-h", "--help", action="help")
    parser.add_option("-p", "--platform",
       action="store", type="string",
       default=None, dest="platform",
       help="Platform Type (default: None, options: dell)"
    )
    parser.add_option("-r", "--release",
        action="store", type="string",
        default="precise", dest="release",
        help='''Distribution release version (default:
                precise, options: lucid, precise)'''
    )
    parser.add_option("-t", "--type",
        action="store", type="string",
        default="generic", dest="sys_type",
        help='''Swift system (options: proxy, storage,
                saio, generic, lb, syslog) Please note
                these must be dsh groups as well'''
    )
    parser.add_option("-c", "--core",
        action="store", type="string",
        default=False, dest="core",
        help="Use central core information (default: False) "
    )
    parser.add_option("-H", "--host",
        action="store", type="string",
        default=None, dest="single_host",
        help="Single host to run the setup against (default: None)"
    )
    parser.add_option("-g", "--dsh-group",
        action="store", type="string",
        default=None, dest="dsh_group",
        help='''Uses the indicated dsh group instead of trying
                to use a group that matches the system type to be
                deployed. Use with care and make sure the group exists
                (default: None)'''
    )
    (options, args) = parser.parse_args()

    '''
    If a host is provided than the setup will
    only happen on this single host as desired
    '''
    if options.single_host:
        host_list = [options.single_host,]
    elif options.dsh_group:
        host_list = generate_hosts_list(options.dsh_group)
    else:
        host_list = generate_hosts_list(options.sys_type)

    '''
    Tasks that would be executed on most nodes with
    perhaps exception of the load balancers
    '''
    execute(add_keyrings, hosts=host_list)
    execute(setup_swiftuser, hosts=host_list)
    execute(do_common_setup, options, hosts=host_list)

    if 'generic' in options.sys_type:
        execute(do_swift_generic_setup, hosts=host_list)

    if 'proxy' in options.sys_type:
        execute(do_swift_proxy_setup, options.sys_type, hosts=host_list)

    if 'storage' in options.sys_type:
        execute(do_swift_storage_setup, options.sys_type, hosts=host_list)

    if 'saio' in options.sys_type:
        execute(do_swift_saio_setup, options.sys_type, hosts=host_list)

    return 0


if __name__ == '__main__':
    status = main()
    disconnect_all()
    sys.exit(status)
