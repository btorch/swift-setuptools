""" See COPYING for license information """

import swiftst.consts as sc
from fabric.api import *
from fabric.network import *


def deploy_tools():
    '''
    This function will add the Dell ubuntu repo file, then
    install the repo key and finally install the tools
    '''
    tools = ['srvadmin-all']

    sudo('''
         echo "deb http://linux.dell.com/repo/community/deb/latest /" >
         /etc/apt/sources.list.d/linux.dell.com.sources.list
        ''')
    sudo('gpg --list-keys >/dev/null')
    sudo('''
         gpg --keyserver pool.sks-keyservers.net
         --recv-key 1285491434D8786F
        ''')
    sudo('gpg -a --export 1285491434D8786F | apt-key add -')
    sudo('apt-get update -qq -o Acquire::http::No-Cache=True ')
    sudo('export DEBIAN_FRONTEND=noninteractive ; apt-get install %s %s '
         % (sc.apt_opts, ' '.join(tools)))
    sudo('/etc/init.d/dataeng restart')
    time.sleep(15)


def disable_attrs():
    '''
    Should not be used yet
    '''
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=NodeInterleave setting=Disabled
        ''')
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=ProcVirtualization setting=Disabled
        ''')
    sudo('''/opt/dell/srvadmin/bin/omconfig chassis biossetup
            attribute=SysProfile setting=PerfOptimized
        ''')
