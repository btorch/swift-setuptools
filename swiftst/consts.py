""" See COPYING for license information. """

'''
Some parameters that are passed over on apt-get installs
'''
apt_opts = ' -y -qq --force-yes -o Dpkg::Options::=--force-confdef '

'''
Keyring packages that might be needed
'''
keyrings = ['ubuntu-cloud-keyring']

'''
Utilities that will be install on all systems by the common setup
'''
general_tools = ['python-software-properties', 'patch', 'debconf',
                 'bonnie++', 'dstat', 'python-configobj', 'curl',
                 'subversion', 'git-core', 'iptraf', 'htop',
                 'nmon', 'strace', 'iotop', 'debsums','python-pip']

'''
Dictionary that contains system:packages that will be installed
for swift according to each system functionality
'''
packages = {'generic': ['swift', 'python-swift', 'python-swiftclient'],
            'proxy': ['swift-proxy'],
            'storage': ['swift-account', 'swift-container', 'swift-object'],
            'saio': ['swift-proxy', 'swift-account', 'swift-container',
                     'swift-object'],
            'other': ['python-suds', 'python-slogging']
            }

'''
This is a dictionary that matches the template files that have
placeholders with the keywords that need to be replacted by what
has been set in the configuration file. The keywords below must
match the keys in the configuration file. The only difference is
that they will be lowecase in the configuration file.
'''
templates = {'common/etc/aliases': ('EMAIL_ADDR', 'PAGER_ADDR'),
             'common/etc/exim4/update-exim4.conf': ('OUTGOING_DOMAIN',
                                                    'SMARTHOST'),
             'common/etc/cron.d/ringverify': ('RINGSERVER_IP', ),
             'admin/srv/ring/scripts/retrievering.sh': ('RINGSERVER_IP', ),
             'common/etc/swift/swift.conf': ('SWIFT_HASH', ),
             'common/etc/syslog-ng/conf.d/swift-syslog-ng.conf': ('SYSLOGS_IP', ),
             'proxy/etc/memcached.conf': ('MEMCACHE_MAXMEM', 'SIM_CONNECTIONS'),
             'proxy/etc/swift/memcache.conf': ('MEMCACHE_SERVER_LIST', ),
             'proxy/etc/swift/proxy-server.conf': ('KEYSTONE_IP',
                                                   'KEYSTONE_PORT',
                                                   'KEYSTONE_AUTH_PROTO',
                                                   'KEYSTONE_AUTH_URI',
                                                   'KEYSTONE_ADMIN_TENANT',
                                                   'KEYSTONE_ADMIN_USER',
                                                   'KEYSTONE_ADMIN_KEY',
                                                   'INFORMANT_IP'),
             'admin/etc/swift/dispersion.conf': ('KEYSTONE_AUTH_URI',
                                                 'KEYSTONE_ADMIN_TENANT',
                                                 'KEYSTONE_ADMIN_USER',
                                                 'KEYSTONE_ADMIN_KEY')
            }
