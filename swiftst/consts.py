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
