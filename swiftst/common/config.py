""" See COPYING for license information """

import sys
import os
from swiftst.exceptions import ConfigFileError
from ConfigParser import ConfigParser


def parse_config(configfile):
    '''
    Takes care of parsing the configuration file
    For now everything falls in the default section but
    will be split later
    '''

    results = {}
    c = ConfigParser()
    if not c.read(configfile):
        status = 204
        msg = "No content found in the config file to be parsed"
        raise ConfigFileError(status, msg)
    else:
        """ Get Defaults """
        conf = dict(c.defaults())
        """Account Info"""
        results['account_number'] = conf.get('account_number','1000') 
        results['account_name'] = conf.get('account_name','sampler')
        results['account_nick'] = conf.get('account_nick','sampler')
        """Email"""
        results['email_addr'] = conf.get('email_addr','me@mydomain.com')
        results['pager_addr'] = conf.get('pager_addr','me@mydomain.com')
        results['smarthost'] = conf.get('smarthost','smart.mydomain.com')
        results['outgoing_domain'] = conf.get('outgoing_domain',
                                              'swift.mydomain.com')
        """IPs"""
        results['admin_ip'] = conf.get('admin_ip','172.16.0.3')
        results['ringserver_ip'] = conf.get('ringserver_ip','172.16.0.3')
        results['syslogs_ip'] = conf.get('syslogs_ip','172.16.0.3')
        results['informant_ip'] = conf.get('informant_ip','172.16.0.3')
        """Swift"""
        results['swift_hash'] = conf.get('swift_hash','supercrypthash')
        results['processing_account'] = conf.get('processing_account',
                                                 'AUTH_nothing')
        results['memcache_server_list'] = conf.get('memcache_server_list',
                                                   '127.0.0.1:11211')
        """Memcache"""
        results['memcache_maxmem'] = conf.get('memcache_maxmem','512')
        results['sim_connections'] = conf.get('sim_connections','1024')
        """Keystone"""
        results['keystone_ip'] = conf.get('keystone_ip','172.16.0.3')
        results['keystone_port'] = conf.get('keystone_port','35357')
        results['keystone_auth_proto'] = conf.get('keystone_auth_proto',
                                                  'http')
        results['keystone_auth_uri'] = conf.get('keystone_auth_uri',
                                                'http://172.16.0.3:5000/')
        results['keystone_admin_tenant'] = conf.get('keystone_admin_tenant',
                                                    'Services')
        results['keystone_admin_user'] = conf.get('keystone_admin_user',
                                                  'swift')
        results['keystone_admin_key'] = conf.get('keystone_admin_key',
                                                 'noswift')

    if c.has_section('generate-configs'):
        conf = dict(c.items('generate-configs'))
        results['template_dir'] = conf.get('template_dir',
                                            '/etc/swift-setuptools/templates')
        results['genconfigs'] = conf.get('generated_configs',
                                         '/tmp/generated_cluster_configs')
    else:
        status = 404
        msg = "No section found for generate-configs in the config file"
        raise ConfigFileError(status, msg)
                
    return results
