#!/usr/bin/env python
# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gettext
from optparse import OptionParser
from os.path import basename
from sys import argv, exit

from swift.common.bufferedhttp import http_connect_raw as http_connect
from swift.common.utils import urlparse

def opt(command):
    gettext.install('swauth', unicode=1)
    parser = OptionParser(usage='Usage: %prog [options] <account> <user> <password>')
    parser.add_option('-a', '--admin', dest='admin', action='store_true',
        default=False, help='Give the user administrator access; otherwise '
        'the user will only have access to containers specifically allowed '
        'with ACLs.')
    parser.add_option('-r', '--reseller-admin', dest='reseller_admin',
        action='store_true', default=False, help='Give the user full reseller '
        'administrator access, giving them full access to all accounts within '
        'the reseller, including the ability to create new accounts. Creating '
        'a new reseller admin requires super_admin rights.')
    parser.add_option('-s', '--suffix', dest='suffix',
        default='', help='The suffix to use with the reseller prefix as the '
        'storage account name (default: <randomly-generated-uuid4>) Note: If '
        'the account already exists, this will have no effect on existing '
        'service URLs. Those will need to be updated with '
        'swauth-set-account-service')
    parser.add_option('-A', '--admin-url', dest='admin_url',
        default='http://127.0.0.1:8080/auth/', help='The URL to the auth '
        'subsystem (default: http://127.0.0.1:8080/auth/')
    parser.add_option('-U', '--admin-user', dest='admin_user',
        default='.super_admin', help='The user with admin rights to add users '
        '(default: .super_admin).')
    parser.add_option('-K', '--admin-key', dest='admin_key',
        help='The key for the user with admin rights to add users.')
    #########################
    # modified by wuzebang 2014/2/27
    #args = argv[1:]
    args = command
    if not args:
        args.append('-h')
    (options, args) = parser.parse_args(args)
    if len(args) < 3:
        parser.parse_args(['-h'])
    elif len(args) == 3:
        attr = []
    else:
        attr = args[3:]
    account, user, password = args[:3]    
    ############################
    
    parsed = urlparse(options.admin_url)
    if parsed.scheme not in ('http', 'https'):
        raise Exception('Cannot handle protocol scheme %s for url %s' %
                        (parsed.scheme, repr(options.admin_url)))
    parsed_path = parsed.path
    if not parsed_path:
        parsed_path = '/'
    elif parsed_path[-1] != '/':
        parsed_path += '/'
    # Ensure the account exists if user is NOT trying to change his password
    if not options.admin_user == (account + ':' + user):
        path = '%sv2/%s' % (parsed_path, account)
        headers = {'X-Auth-Admin-User': options.admin_user,
                   'X-Auth-Admin-Key': options.admin_key}
        if options.suffix:
            headers['X-Account-Suffix'] = options.suffix
        conn = http_connect(parsed.hostname, parsed.port, 'GET', path, headers,
                            ssl=(parsed.scheme == 'https'))
        resp = conn.getresponse()
        if resp.status // 100 != 2:
            headers['Content-Length'] = '0'
            conn = http_connect(parsed.hostname, parsed.port, 'PUT', path, headers,
                                ssl=(parsed.scheme == 'https'))
            resp = conn.getresponse()
            if resp.status // 100 != 2:
                print 'Account creation failed: %s %s' % (resp.status, resp.reason)
    # Add the user
    path = '%sv2/%s/%s' % (parsed_path, account, user)
    headers = {'X-Auth-Admin-User': options.admin_user,
               'X-Auth-Admin-Key': options.admin_key,
               'X-Auth-User-Key': password,
               'X-Auth-User-Attr': attr,    # added by wuzbeang 2014/2/27
               'Content-Length': '0'}
    
    print 'the header is :\n' , repr(headers)
            
    if options.admin:
        headers['X-Auth-User-Admin'] = 'true'
    if options.reseller_admin:
        headers['X-Auth-User-Reseller-Admin'] = 'true'
    conn = http_connect(parsed.hostname, parsed.port, 'PUT', path, headers,
                        ssl=(parsed.scheme == 'https'))
    resp = conn.getresponse()
    
    if resp.status // 100 != 2:
        #exit('User creation failed: %s %s' % (resp.status, resp.reason))
        print 'User added failed!'  

# if __name__ == '__main__':
#     command = ['-A', 'http://127.0.0.1:8080/auth/', '-K', 'swauthkey', '-a', 'test', 'one', 'one', 'at1', 'at2']
#     opt(command)
