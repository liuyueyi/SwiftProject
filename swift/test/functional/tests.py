#!/usr/bin/python -u
# Copyright (c) 2010-2012 OpenStack Foundation
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

from datetime import datetime
import hashlib
import json
import locale
import random
import StringIO
import time
import threading
import uuid
import unittest
from nose import SkipTest
from ConfigParser import ConfigParser

from test import get_config
from test.functional.swift_test_client import Account, Connection, File, \
    ResponseError
from swift.common.constraints import MAX_FILE_SIZE, MAX_META_NAME_LENGTH, \
    MAX_META_VALUE_LENGTH, MAX_META_COUNT, MAX_META_OVERALL_SIZE, \
    MAX_OBJECT_NAME_LENGTH, CONTAINER_LISTING_LIMIT, ACCOUNT_LISTING_LIMIT, \
    MAX_ACCOUNT_NAME_LENGTH, MAX_CONTAINER_NAME_LENGTH

default_constraints = dict((
    ('max_file_size', MAX_FILE_SIZE),
    ('max_meta_name_length', MAX_META_NAME_LENGTH),
    ('max_meta_value_length', MAX_META_VALUE_LENGTH),
    ('max_meta_count', MAX_META_COUNT),
    ('max_meta_overall_size', MAX_META_OVERALL_SIZE),
    ('max_object_name_length', MAX_OBJECT_NAME_LENGTH),
    ('container_listing_limit', CONTAINER_LISTING_LIMIT),
    ('account_listing_limit', ACCOUNT_LISTING_LIMIT),
    ('max_account_name_length', MAX_ACCOUNT_NAME_LENGTH),
    ('max_container_name_length', MAX_CONTAINER_NAME_LENGTH)))
constraints_conf = ConfigParser()
conf_exists = constraints_conf.read('/etc/swift/swift.conf')
# Constraints are set first from the test config, then from
# /etc/swift/swift.conf if it exists. If swift.conf doesn't exist,
# then limit test coverage. This allows SAIO tests to work fine but
# requires remote functional testing to know something about the cluster
# that is being tested.
config = get_config('func_test')
for k in default_constraints:
    if k in config:
        # prefer what's in test.conf
        config[k] = int(config[k])
    elif conf_exists:
        # swift.conf exists, so use what's defined there (or swift defaults)
        # This normally happens when the test is running locally to the cluster
        # as in a SAIO.
        config[k] = default_constraints[k]
    else:
        # .functests don't know what the constraints of the tested cluster are,
        # so the tests can't reliably pass or fail. Therefore, skip those
        # tests.
        config[k] = '%s constraint is not defined' % k

web_front_end = config.get('web_front_end', 'integral')
normalized_urls = config.get('normalized_urls', False)


def load_constraint(name):
    c = config[name]
    if not isinstance(c, int):
        raise SkipTest(c)
    return c

locale.setlocale(locale.LC_COLLATE, config.get('collate', 'C'))


def chunks(s, length=3):
    i, j = 0, length
    while i < len(s):
        yield s[i:j]
        i, j = j, j + length


def timeout(seconds, method, *args, **kwargs):
    class TimeoutThread(threading.Thread):
        def __init__(self, method, *args, **kwargs):
            threading.Thread.__init__(self)

            self.method = method
            self.args = args
            self.kwargs = kwargs
            self.exception = None

        def run(self):
            try:
                self.method(*self.args, **self.kwargs)
            except Exception as e:
                self.exception = e

    t = TimeoutThread(method, *args, **kwargs)
    t.start()
    t.join(seconds)

    if t.exception:
        raise t.exception

    if t.isAlive():
        t._Thread__stop()
        return True
    return False


class Utils:
    @classmethod
    def create_ascii_name(cls, length=None):
        return uuid.uuid4().hex

    @classmethod
    def create_utf8_name(cls, length=None):
        if length is None:
            length = 15
        else:
            length = int(length)

        utf8_chars = u'\uF10F\uD20D\uB30B\u9409\u8508\u5605\u3703\u1801'\
                     u'\u0900\uF110\uD20E\uB30C\u940A\u8509\u5606\u3704'\
                     u'\u1802\u0901\uF111\uD20F\uB30D\u940B\u850A\u5607'\
                     u'\u3705\u1803\u0902\uF112\uD210\uB30E\u940C\u850B'\
                     u'\u5608\u3706\u1804\u0903\u03A9\u2603'
        return ''.join([random.choice(utf8_chars)
                        for x in xrange(length)]).encode('utf-8')

    create_name = create_ascii_name


class Base(unittest.TestCase):
    def setUp(self):
        cls = type(self)
        if not cls.set_up:
            cls.env.setUp()
            cls.set_up = True

    def assert_body(self, body):
        response_body = self.env.conn.response.read()
        self.assert_(response_body == body,
                     'Body returned: %s' % (response_body))

    def assert_status(self, status_or_statuses):
        self.assert_(self.env.conn.response.status == status_or_statuses or
                     (hasattr(status_or_statuses, '__iter__') and
                      self.env.conn.response.status in status_or_statuses),
                     'Status returned: %d Expected: %s' %
                     (self.env.conn.response.status, status_or_statuses))


class Base2(object):
    def setUp(self):
        Utils.create_name = Utils.create_utf8_name
        super(Base2, self).setUp()

    def tearDown(self):
        Utils.create_name = Utils.create_ascii_name


class TestAccountEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.containers = []
        for i in range(10):
            cont = cls.account.container(Utils.create_name())
            if not cont.create():
                raise ResponseError(cls.conn.response)

            cls.containers.append(cont)


class TestAccountDev(Base):
    env = TestAccountEnv
    set_up = False


class TestAccountDevUTF8(Base2, TestAccountDev):
    set_up = False


class TestAccount(Base):
    env = TestAccountEnv
    set_up = False

    def testNoAuthToken(self):
        self.assertRaises(ResponseError, self.env.account.info,
                          cfg={'no_auth_token': True})
        self.assert_status([401, 412])

        self.assertRaises(ResponseError, self.env.account.containers,
                          cfg={'no_auth_token': True})
        self.assert_status([401, 412])

    def testInvalidUTF8Path(self):
        invalid_utf8 = Utils.create_utf8_name()[::-1]
        container = self.env.account.container(invalid_utf8)
        self.assert_(not container.create(cfg={'no_path_quote': True}))
        self.assert_status(412)
        self.assert_body('Invalid UTF8 or contains NULL')

    def testVersionOnlyPath(self):
        self.env.account.conn.make_request('PUT',
                                           cfg={'version_only_path': True})
        self.assert_status(412)
        self.assert_body('Bad URL')

    def testInvalidPath(self):
        was_url = self.env.account.conn.storage_url
        if (normalized_urls):
            self.env.account.conn.storage_url = '/'
        else:
            self.env.account.conn.storage_url = "/%s" % was_url
        self.env.account.conn.make_request('GET')
        try:
            self.assert_status(404)
        finally:
            self.env.account.conn.storage_url = was_url

    def testPUT(self):
        self.env.account.conn.make_request('PUT')
        self.assert_status([403, 405])

    def testAccountHead(self):
        try_count = 0
        while try_count < 5:
            try_count += 1

            info = self.env.account.info()
            for field in ['object_count', 'container_count', 'bytes_used']:
                self.assert_(info[field] >= 0)

            if info['container_count'] == len(self.env.containers):
                break

            if try_count < 5:
                time.sleep(1)

        self.assertEquals(info['container_count'], len(self.env.containers))
        self.assert_status(204)

    def testContainerSerializedInfo(self):
        container_info = {}
        for container in self.env.containers:
            info = {'bytes': 0}
            info['count'] = random.randint(10, 30)
            for i in range(info['count']):
                file_item = container.file(Utils.create_name())
                bytes = random.randint(1, 32768)
                file_item.write_random(bytes)
                info['bytes'] += bytes

            container_info[container.name] = info

        for format_type in ['json', 'xml']:
            for a in self.env.account.containers(
                    parms={'format': format_type}):
                self.assert_(a['count'] >= 0)
                self.assert_(a['bytes'] >= 0)

            headers = dict(self.env.conn.response.getheaders())
            if format_type == 'json':
                self.assertEquals(headers['content-type'],
                                  'application/json; charset=utf-8')
            elif format_type == 'xml':
                self.assertEquals(headers['content-type'],
                                  'application/xml; charset=utf-8')

    def testListingLimit(self):
        limit = load_constraint('account_listing_limit')
        for l in (1, 100, limit / 2, limit - 1, limit, limit + 1, limit * 2):
            p = {'limit': l}

            if l <= limit:
                self.assert_(len(self.env.account.containers(parms=p)) <= l)
                self.assert_status(200)
            else:
                self.assertRaises(ResponseError,
                                  self.env.account.containers, parms=p)
                self.assert_status(412)

    def testContainerListing(self):
        a = sorted([c.name for c in self.env.containers])

        for format_type in [None, 'json', 'xml']:
            b = self.env.account.containers(parms={'format': format_type})

            if isinstance(b[0], dict):
                b = [x['name'] for x in b]

            self.assertEquals(a, b)

    def testInvalidAuthToken(self):
        hdrs = {'X-Auth-Token': 'bogus_auth_token'}
        self.assertRaises(ResponseError, self.env.account.info, hdrs=hdrs)
        self.assert_status(401)

    def testLastContainerMarker(self):
        for format_type in [None, 'json', 'xml']:
            containers = self.env.account.containers({'format': format_type})
            self.assertEquals(len(containers), len(self.env.containers))
            self.assert_status(200)

            containers = self.env.account.containers(
                parms={'format': format_type, 'marker': containers[-1]})
            self.assertEquals(len(containers), 0)
            if format_type is None:
                self.assert_status(204)
            else:
                self.assert_status(200)

    def testMarkerLimitContainerList(self):
        for format_type in [None, 'json', 'xml']:
            for marker in ['0', 'A', 'I', 'R', 'Z', 'a', 'i', 'r', 'z',
                           'abc123', 'mnop', 'xyz']:

                limit = random.randint(2, 9)
                containers = self.env.account.containers(
                    parms={'format': format_type,
                           'marker': marker,
                           'limit': limit})
                self.assert_(len(containers) <= limit)
                if containers:
                    if isinstance(containers[0], dict):
                        containers = [x['name'] for x in containers]
                    self.assert_(locale.strcoll(containers[0], marker) > 0)

    def testContainersOrderedByName(self):
        for format_type in [None, 'json', 'xml']:
            containers = self.env.account.containers(
                parms={'format': format_type})
            if isinstance(containers[0], dict):
                containers = [x['name'] for x in containers]
            self.assertEquals(sorted(containers, cmp=locale.strcoll),
                              containers)


class TestAccountUTF8(Base2, TestAccount):
    set_up = False


class TestAccountNoContainersEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()


class TestAccountNoContainers(Base):
    env = TestAccountNoContainersEnv
    set_up = False

    def testGetRequest(self):
        for format_type in [None, 'json', 'xml']:
            self.assert_(not self.env.account.containers(
                parms={'format': format_type}))

            if format_type is None:
                self.assert_status(204)
            else:
                self.assert_status(200)


class TestAccountNoContainersUTF8(Base2, TestAccountNoContainers):
    set_up = False


class TestContainerEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.container = cls.account.container(Utils.create_name())
        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        cls.file_count = 10
        cls.file_size = 128
        cls.files = list()
        for x in range(cls.file_count):
            file_item = cls.container.file(Utils.create_name())
            file_item.write_random(cls.file_size)
            cls.files.append(file_item.name)


class TestContainerDev(Base):
    env = TestContainerEnv
    set_up = False


class TestContainerDevUTF8(Base2, TestContainerDev):
    set_up = False


class TestContainer(Base):
    env = TestContainerEnv
    set_up = False

    def testContainerNameLimit(self):
        limit = load_constraint('max_container_name_length')

        for l in (limit - 100, limit - 10, limit - 1, limit,
                  limit + 1, limit + 10, limit + 100):
            cont = self.env.account.container('a' * l)
            if l <= limit:
                self.assert_(cont.create())
                self.assert_status(201)
            else:
                self.assert_(not cont.create())
                self.assert_status(400)

    def testFileThenContainerDelete(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())
        file_item = cont.file(Utils.create_name())
        self.assert_(file_item.write_random())

        self.assert_(file_item.delete())
        self.assert_status(204)
        self.assert_(file_item.name not in cont.files())

        self.assert_(cont.delete())
        self.assert_status(204)
        self.assert_(cont.name not in self.env.account.containers())

    def testFileListingLimitMarkerPrefix(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())

        files = sorted([Utils.create_name() for x in xrange(10)])
        for f in files:
            file_item = cont.file(f)
            self.assert_(file_item.write_random())

        for i in xrange(len(files)):
            f = files[i]
            for j in xrange(1, len(files) - i):
                self.assert_(cont.files(parms={'limit': j, 'marker': f}) ==
                             files[i + 1: i + j + 1])
            self.assert_(cont.files(parms={'marker': f}) == files[i + 1:])
            self.assert_(cont.files(parms={'marker': f, 'prefix': f}) == [])
            self.assert_(cont.files(parms={'prefix': f}) == [f])

    def testPrefixAndLimit(self):
        load_constraint('container_listing_limit')
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())

        prefix_file_count = 10
        limit_count = 2
        prefixs = ['alpha/', 'beta/', 'kappa/']
        prefix_files = {}

        for prefix in prefixs:
            prefix_files[prefix] = []

            for i in range(prefix_file_count):
                file_item = cont.file(prefix + Utils.create_name())
                file_item.write()
                prefix_files[prefix].append(file_item.name)

        for format_type in [None, 'json', 'xml']:
            for prefix in prefixs:
                files = cont.files(parms={'prefix': prefix})
                self.assertEquals(files, sorted(prefix_files[prefix]))

        for format_type in [None, 'json', 'xml']:
            for prefix in prefixs:
                files = cont.files(parms={'limit': limit_count,
                                   'prefix': prefix})
                self.assertEquals(len(files), limit_count)

                for file_item in files:
                    self.assert_(file_item.startswith(prefix))

    def testCreate(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())
        self.assert_status(201)
        self.assert_(cont.name in self.env.account.containers())

    def testContainerFileListOnContainerThatDoesNotExist(self):
        for format_type in [None, 'json', 'xml']:
            container = self.env.account.container(Utils.create_name())
            self.assertRaises(ResponseError, container.files,
                              parms={'format': format_type})
            self.assert_status(404)

    def testUtf8Container(self):
        valid_utf8 = Utils.create_utf8_name()
        invalid_utf8 = valid_utf8[::-1]
        container = self.env.account.container(valid_utf8)
        self.assert_(container.create(cfg={'no_path_quote': True}))
        self.assert_(container.name in self.env.account.containers())
        self.assertEquals(container.files(), [])
        self.assert_(container.delete())

        container = self.env.account.container(invalid_utf8)
        self.assert_(not container.create(cfg={'no_path_quote': True}))
        self.assert_status(412)
        self.assertRaises(ResponseError, container.files,
                          cfg={'no_path_quote': True})
        self.assert_status(412)

    def testCreateOnExisting(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())
        self.assert_status(201)
        self.assert_(cont.create())
        self.assert_status(202)

    def testSlashInName(self):
        if Utils.create_name == Utils.create_utf8_name:
            cont_name = list(unicode(Utils.create_name(), 'utf-8'))
        else:
            cont_name = list(Utils.create_name())

        cont_name[random.randint(2, len(cont_name) - 2)] = '/'
        cont_name = ''.join(cont_name)

        if Utils.create_name == Utils.create_utf8_name:
            cont_name = cont_name.encode('utf-8')

        cont = self.env.account.container(cont_name)
        self.assert_(not cont.create(cfg={'no_path_quote': True}),
                     'created container with name %s' % (cont_name))
        self.assert_status(404)
        self.assert_(cont.name not in self.env.account.containers())

    def testDelete(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())
        self.assert_status(201)
        self.assert_(cont.delete())
        self.assert_status(204)
        self.assert_(cont.name not in self.env.account.containers())

    def testDeleteOnContainerThatDoesNotExist(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(not cont.delete())
        self.assert_status(404)

    def testDeleteOnContainerWithFiles(self):
        cont = self.env.account.container(Utils.create_name())
        self.assert_(cont.create())
        file_item = cont.file(Utils.create_name())
        file_item.write_random(self.env.file_size)
        self.assert_(file_item.name in cont.files())
        self.assert_(not cont.delete())
        self.assert_status(409)

    def testFileCreateInContainerThatDoesNotExist(self):
        file_item = File(self.env.conn, self.env.account, Utils.create_name(),
                         Utils.create_name())
        self.assertRaises(ResponseError, file_item.write)
        self.assert_status(404)

    def testLastFileMarker(self):
        for format_type in [None, 'json', 'xml']:
            files = self.env.container.files({'format': format_type})
            self.assertEquals(len(files), len(self.env.files))
            self.assert_status(200)

            files = self.env.container.files(
                parms={'format': format_type, 'marker': files[-1]})
            self.assertEquals(len(files), 0)

            if format_type is None:
                self.assert_status(204)
            else:
                self.assert_status(200)

    def testContainerFileList(self):
        for format_type in [None, 'json', 'xml']:
            files = self.env.container.files(parms={'format': format_type})
            self.assert_status(200)
            if isinstance(files[0], dict):
                files = [x['name'] for x in files]

            for file_item in self.env.files:
                self.assert_(file_item in files)

            for file_item in files:
                self.assert_(file_item in self.env.files)

    def testMarkerLimitFileList(self):
        for format_type in [None, 'json', 'xml']:
            for marker in ['0', 'A', 'I', 'R', 'Z', 'a', 'i', 'r', 'z',
                           'abc123', 'mnop', 'xyz']:
                limit = random.randint(2, self.env.file_count - 1)
                files = self.env.container.files(parms={'format': format_type,
                                                        'marker': marker,
                                                        'limit': limit})

                if not files:
                    continue

                if isinstance(files[0], dict):
                    files = [x['name'] for x in files]

                self.assert_(len(files) <= limit)
                if files:
                    if isinstance(files[0], dict):
                        files = [x['name'] for x in files]
                    self.assert_(locale.strcoll(files[0], marker) > 0)

    def testFileOrder(self):
        for format_type in [None, 'json', 'xml']:
            files = self.env.container.files(parms={'format': format_type})
            if isinstance(files[0], dict):
                files = [x['name'] for x in files]
            self.assertEquals(sorted(files, cmp=locale.strcoll), files)

    def testContainerInfo(self):
        info = self.env.container.info()
        self.assert_status(204)
        self.assertEquals(info['object_count'], self.env.file_count)
        self.assertEquals(info['bytes_used'],
                          self.env.file_count * self.env.file_size)

    def testContainerInfoOnContainerThatDoesNotExist(self):
        container = self.env.account.container(Utils.create_name())
        self.assertRaises(ResponseError, container.info)
        self.assert_status(404)

    def testContainerFileListWithLimit(self):
        for format_type in [None, 'json', 'xml']:
            files = self.env.container.files(parms={'format': format_type,
                                                    'limit': 2})
            self.assertEquals(len(files), 2)

    def testTooLongName(self):
        cont = self.env.account.container('x' * 257)
        self.assert_(not cont.create(),
                     'created container with name %s' % (cont.name))
        self.assert_status(400)

    def testContainerExistenceCachingProblem(self):
        cont = self.env.account.container(Utils.create_name())
        self.assertRaises(ResponseError, cont.files)
        self.assert_(cont.create())
        cont.files()

        cont = self.env.account.container(Utils.create_name())
        self.assertRaises(ResponseError, cont.files)
        self.assert_(cont.create())
        file_item = cont.file(Utils.create_name())
        file_item.write_random()


class TestContainerUTF8(Base2, TestContainer):
    set_up = False


class TestContainerPathsEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.file_size = 8

        cls.container = cls.account.container(Utils.create_name())
        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        cls.files = [
            '/file1',
            '/file A',
            '/dir1/',
            '/dir2/',
            '/dir1/file2',
            '/dir1/subdir1/',
            '/dir1/subdir2/',
            '/dir1/subdir1/file2',
            '/dir1/subdir1/file3',
            '/dir1/subdir1/file4',
            '/dir1/subdir1/subsubdir1/',
            '/dir1/subdir1/subsubdir1/file5',
            '/dir1/subdir1/subsubdir1/file6',
            '/dir1/subdir1/subsubdir1/file7',
            '/dir1/subdir1/subsubdir1/file8',
            '/dir1/subdir1/subsubdir2/',
            '/dir1/subdir1/subsubdir2/file9',
            '/dir1/subdir1/subsubdir2/file0',
            'file1',
            'dir1/',
            'dir2/',
            'dir1/file2',
            'dir1/subdir1/',
            'dir1/subdir2/',
            'dir1/subdir1/file2',
            'dir1/subdir1/file3',
            'dir1/subdir1/file4',
            'dir1/subdir1/subsubdir1/',
            'dir1/subdir1/subsubdir1/file5',
            'dir1/subdir1/subsubdir1/file6',
            'dir1/subdir1/subsubdir1/file7',
            'dir1/subdir1/subsubdir1/file8',
            'dir1/subdir1/subsubdir2/',
            'dir1/subdir1/subsubdir2/file9',
            'dir1/subdir1/subsubdir2/file0',
            'dir1/subdir with spaces/',
            'dir1/subdir with spaces/file B',
            'dir1/subdir+with{whatever/',
            'dir1/subdir+with{whatever/file D',
        ]

        stored_files = set()
        for f in cls.files:
            file_item = cls.container.file(f)
            if f.endswith('/'):
                file_item.write(hdrs={'Content-Type': 'application/directory'})
            else:
                file_item.write_random(cls.file_size,
                                       hdrs={'Content-Type':
                                             'application/directory'})
            if (normalized_urls):
                nfile = '/'.join(filter(None, f.split('/')))
                if (f[-1] == '/'):
                    nfile += '/'
                stored_files.add(nfile)
            else:
                stored_files.add(f)
        cls.stored_files = sorted(stored_files)


class TestContainerPaths(Base):
    env = TestContainerPathsEnv
    set_up = False

    def testTraverseContainer(self):
        found_files = []
        found_dirs = []

        def recurse_path(path, count=0):
            if count > 10:
                raise ValueError('too deep recursion')

            for file_item in self.env.container.files(parms={'path': path}):
                self.assert_(file_item.startswith(path))
                if file_item.endswith('/'):
                    recurse_path(file_item, count + 1)
                    found_dirs.append(file_item)
                else:
                    found_files.append(file_item)

        recurse_path('')
        for file_item in self.env.stored_files:
            if file_item.startswith('/'):
                self.assert_(file_item not in found_dirs)
                self.assert_(file_item not in found_files)
            elif file_item.endswith('/'):
                self.assert_(file_item in found_dirs)
                self.assert_(file_item not in found_files)
            else:
                self.assert_(file_item in found_files)
                self.assert_(file_item not in found_dirs)

        found_files = []
        found_dirs = []
        recurse_path('/')
        for file_item in self.env.stored_files:
            if not file_item.startswith('/'):
                self.assert_(file_item not in found_dirs)
                self.assert_(file_item not in found_files)
            elif file_item.endswith('/'):
                self.assert_(file_item in found_dirs)
                self.assert_(file_item not in found_files)
            else:
                self.assert_(file_item in found_files)
                self.assert_(file_item not in found_dirs)

    def testContainerListing(self):
        for format_type in (None, 'json', 'xml'):
            files = self.env.container.files(parms={'format': format_type})

            if isinstance(files[0], dict):
                files = [str(x['name']) for x in files]

            self.assertEquals(files, self.env.stored_files)

        for format_type in ('json', 'xml'):
            for file_item in self.env.container.files(parms={'format':
                                                             format_type}):
                self.assert_(int(file_item['bytes']) >= 0)
                self.assert_('last_modified' in file_item)
                if file_item['name'].endswith('/'):
                    self.assertEquals(file_item['content_type'],
                                      'application/directory')

    def testStructure(self):
        def assert_listing(path, file_list):
            files = self.env.container.files(parms={'path': path})
            self.assertEquals(sorted(file_list, cmp=locale.strcoll), files)
        if not normalized_urls:
            assert_listing('/', ['/dir1/', '/dir2/', '/file1', '/file A'])
            assert_listing('/dir1',
                           ['/dir1/file2', '/dir1/subdir1/', '/dir1/subdir2/'])
            assert_listing('/dir1/',
                           ['/dir1/file2', '/dir1/subdir1/', '/dir1/subdir2/'])
            assert_listing('/dir1/subdir1',
                           ['/dir1/subdir1/subsubdir2/', '/dir1/subdir1/file2',
                            '/dir1/subdir1/file3', '/dir1/subdir1/file4',
                            '/dir1/subdir1/subsubdir1/'])
            assert_listing('/dir1/subdir2', [])
            assert_listing('', ['file1', 'dir1/', 'dir2/'])
        else:
            assert_listing('', ['file1', 'dir1/', 'dir2/', 'file A'])
        assert_listing('dir1', ['dir1/file2', 'dir1/subdir1/',
                                'dir1/subdir2/', 'dir1/subdir with spaces/',
                                'dir1/subdir+with{whatever/'])
        assert_listing('dir1/subdir1',
                       ['dir1/subdir1/file4', 'dir1/subdir1/subsubdir2/',
                        'dir1/subdir1/file2', 'dir1/subdir1/file3',
                        'dir1/subdir1/subsubdir1/'])
        assert_listing('dir1/subdir1/subsubdir1',
                       ['dir1/subdir1/subsubdir1/file7',
                        'dir1/subdir1/subsubdir1/file5',
                        'dir1/subdir1/subsubdir1/file8',
                        'dir1/subdir1/subsubdir1/file6'])
        assert_listing('dir1/subdir1/subsubdir1/',
                       ['dir1/subdir1/subsubdir1/file7',
                        'dir1/subdir1/subsubdir1/file5',
                        'dir1/subdir1/subsubdir1/file8',
                        'dir1/subdir1/subsubdir1/file6'])
        assert_listing('dir1/subdir with spaces/',
                       ['dir1/subdir with spaces/file B'])


class TestFileEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.container = cls.account.container(Utils.create_name())
        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        cls.file_size = 128


class TestFileDev(Base):
    env = TestFileEnv
    set_up = False


class TestFileDevUTF8(Base2, TestFileDev):
    set_up = False


class TestFile(Base):
    env = TestFileEnv
    set_up = False

    def testCopy(self):
        # makes sure to test encoded characters
        source_filename = 'dealde%2Fl04 011e%204c8df/flash.png'
        file_item = self.env.container.file(source_filename)

        metadata = {}
        for i in range(1):
            metadata[Utils.create_ascii_name()] = Utils.create_name()

        data = file_item.write_random()
        file_item.sync_metadata(metadata)

        dest_cont = self.env.account.container(Utils.create_name())
        self.assert_(dest_cont.create())

        # copy both from within and across containers
        for cont in (self.env.container, dest_cont):
            # copy both with and without initial slash
            for prefix in ('', '/'):
                dest_filename = Utils.create_name()

                file_item = self.env.container.file(source_filename)
                file_item.copy('%s%s' % (prefix, cont), dest_filename)

                self.assert_(dest_filename in cont.files())

                file_item = cont.file(dest_filename)

                self.assert_(data == file_item.read())
                self.assert_(file_item.initialize())
                self.assert_(metadata == file_item.metadata)

    def testCopy404s(self):
        source_filename = Utils.create_name()
        file_item = self.env.container.file(source_filename)
        file_item.write_random()

        dest_cont = self.env.account.container(Utils.create_name())
        self.assert_(dest_cont.create())

        for prefix in ('', '/'):
            # invalid source container
            source_cont = self.env.account.container(Utils.create_name())
            file_item = source_cont.file(source_filename)
            self.assert_(not file_item.copy(
                '%s%s' % (prefix, self.env.container),
                Utils.create_name()))
            self.assert_status(404)

            self.assert_(not file_item.copy('%s%s' % (prefix, dest_cont),
                                            Utils.create_name()))
            self.assert_status(404)

            # invalid source object
            file_item = self.env.container.file(Utils.create_name())
            self.assert_(not file_item.copy(
                '%s%s' % (prefix, self.env.container),
                Utils.create_name()))
            self.assert_status(404)

            self.assert_(not file_item.copy('%s%s' % (prefix, dest_cont),
                                            Utils.create_name()))
            self.assert_status(404)

            # invalid destination container
            file_item = self.env.container.file(source_filename)
            self.assert_(not file_item.copy(
                '%s%s' % (prefix, Utils.create_name()),
                Utils.create_name()))

    def testCopyNoDestinationHeader(self):
        source_filename = Utils.create_name()
        file_item = self.env.container.file(source_filename)
        file_item.write_random()

        file_item = self.env.container.file(source_filename)
        self.assert_(not file_item.copy(Utils.create_name(),
                     Utils.create_name(),
                     cfg={'no_destination': True}))
        self.assert_status(412)

    def testCopyDestinationSlashProblems(self):
        source_filename = Utils.create_name()
        file_item = self.env.container.file(source_filename)
        file_item.write_random()

        # no slash
        self.assert_(not file_item.copy(Utils.create_name(),
                     Utils.create_name(),
                     cfg={'destination': Utils.create_name()}))
        self.assert_status(412)

    def testCopyFromHeader(self):
        source_filename = Utils.create_name()
        file_item = self.env.container.file(source_filename)

        metadata = {}
        for i in range(1):
            metadata[Utils.create_ascii_name()] = Utils.create_name()
        file_item.metadata = metadata

        data = file_item.write_random()

        dest_cont = self.env.account.container(Utils.create_name())
        self.assert_(dest_cont.create())

        # copy both from within and across containers
        for cont in (self.env.container, dest_cont):
            # copy both with and without initial slash
            for prefix in ('', '/'):
                dest_filename = Utils.create_name()

                file_item = cont.file(dest_filename)
                file_item.write(hdrs={'X-Copy-From': '%s%s/%s' % (
                    prefix, self.env.container.name, source_filename)})

                self.assert_(dest_filename in cont.files())

                file_item = cont.file(dest_filename)

                self.assert_(data == file_item.read())
                self.assert_(file_item.initialize())
                self.assert_(metadata == file_item.metadata)

    def testCopyFromHeader404s(self):
        source_filename = Utils.create_name()
        file_item = self.env.container.file(source_filename)
        file_item.write_random()

        for prefix in ('', '/'):
            # invalid source container
            file_item = self.env.container.file(Utils.create_name())
            self.assertRaises(ResponseError, file_item.write,
                              hdrs={'X-Copy-From': '%s%s/%s' %
                              (prefix,
                               Utils.create_name(), source_filename)})
            self.assert_status(404)

            # invalid source object
            file_item = self.env.container.file(Utils.create_name())
            self.assertRaises(ResponseError, file_item.write,
                              hdrs={'X-Copy-From': '%s%s/%s' %
                              (prefix,
                               self.env.container.name, Utils.create_name())})
            self.assert_status(404)

            # invalid destination container
            dest_cont = self.env.account.container(Utils.create_name())
            file_item = dest_cont.file(Utils.create_name())
            self.assertRaises(ResponseError, file_item.write,
                              hdrs={'X-Copy-From': '%s%s/%s' %
                              (prefix,
                               self.env.container.name, source_filename)})
            self.assert_status(404)

    def testNameLimit(self):
        limit = load_constraint('max_object_name_length')

        for l in (1, 10, limit / 2, limit - 1, limit, limit + 1, limit * 2):
            file_item = self.env.container.file('a' * l)

            if l <= limit:
                self.assert_(file_item.write())
                self.assert_status(201)
            else:
                self.assertRaises(ResponseError, file_item.write)
                self.assert_status(400)

    def testQuestionMarkInName(self):
        if Utils.create_name == Utils.create_ascii_name:
            file_name = list(Utils.create_name())
            file_name[random.randint(2, len(file_name) - 2)] = '?'
            file_name = "".join(file_name)
        else:
            file_name = Utils.create_name(6) + '?' + Utils.create_name(6)

        file_item = self.env.container.file(file_name)
        self.assert_(file_item.write(cfg={'no_path_quote': True}))
        self.assert_(file_name not in self.env.container.files())
        self.assert_(file_name.split('?')[0] in self.env.container.files())

    def testDeleteThen404s(self):
        file_item = self.env.container.file(Utils.create_name())
        self.assert_(file_item.write_random())
        self.assert_status(201)

        self.assert_(file_item.delete())
        self.assert_status(204)

        file_item.metadata = {Utils.create_ascii_name(): Utils.create_name()}

        for method in (file_item.info,
                       file_item.read,
                       file_item.sync_metadata,
                       file_item.delete):
            self.assertRaises(ResponseError, method)
            self.assert_status(404)

    def testBlankMetadataName(self):
        file_item = self.env.container.file(Utils.create_name())
        file_item.metadata = {'': Utils.create_name()}
        self.assertRaises(ResponseError, file_item.write_random)
        self.assert_status(400)

    def testMetadataNumberLimit(self):
        number_limit = load_constraint('max_meta_count')
        size_limit = load_constraint('max_meta_overall_size')

        for i in (number_limit - 10, number_limit - 1, number_limit,
                  number_limit + 1, number_limit + 10, number_limit + 100):

            j = size_limit / (i * 2)

            size = 0
            metadata = {}
            while len(metadata.keys()) < i:
                key = Utils.create_ascii_name()
                val = Utils.create_name()

                if len(key) > j:
                    key = key[:j]
                    val = val[:j]

                size += len(key) + len(val)
                metadata[key] = val

            file_item = self.env.container.file(Utils.create_name())
            file_item.metadata = metadata

            if i <= number_limit:
                self.assert_(file_item.write())
                self.assert_status(201)
                self.assert_(file_item.sync_metadata())
                self.assert_status((201, 202))
            else:
                self.assertRaises(ResponseError, file_item.write)
                self.assert_status(400)
                file_item.metadata = {}
                self.assert_(file_item.write())
                self.assert_status(201)
                file_item.metadata = metadata
                self.assertRaises(ResponseError, file_item.sync_metadata)
                self.assert_status(400)

    def testContentTypeGuessing(self):
        file_types = {'wav': 'audio/x-wav', 'txt': 'text/plain',
                      'zip': 'application/zip'}

        container = self.env.account.container(Utils.create_name())
        self.assert_(container.create())

        for i in file_types.keys():
            file_item = container.file(Utils.create_name() + '.' + i)
            file_item.write('', cfg={'no_content_type': True})

        file_types_read = {}
        for i in container.files(parms={'format': 'json'}):
            file_types_read[i['name'].split('.')[1]] = i['content_type']

        self.assertEquals(file_types, file_types_read)

    def testRangedGets(self):
        file_length = 10000
        range_size = file_length / 10
        file_item = self.env.container.file(Utils.create_name())
        data = file_item.write_random(file_length)

        for i in range(0, file_length, range_size):
            range_string = 'bytes=%d-%d' % (i, i + range_size - 1)
            hdrs = {'Range': range_string}
            self.assert_(data[i: i + range_size] == file_item.read(hdrs=hdrs),
                         range_string)

            range_string = 'bytes=-%d' % (i)
            hdrs = {'Range': range_string}
            if i == 0:
                # RFC 2616 14.35.1
                # "If a syntactically valid byte-range-set includes ... at
                # least one suffix-byte-range-spec with a NON-ZERO
                # suffix-length, then the byte-range-set is satisfiable.
                # Otherwise, the byte-range-set is unsatisfiable.
                self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
                self.assert_status(416)
            else:
                self.assertEquals(file_item.read(hdrs=hdrs), data[-i:])

            range_string = 'bytes=%d-' % (i)
            hdrs = {'Range': range_string}
            self.assert_(file_item.read(hdrs=hdrs) == data[i - file_length:],
                         range_string)

        range_string = 'bytes=%d-%d' % (file_length + 1000, file_length + 2000)
        hdrs = {'Range': range_string}
        self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
        self.assert_status(416)

        range_string = 'bytes=%d-%d' % (file_length - 1000, file_length + 2000)
        hdrs = {'Range': range_string}
        self.assert_(file_item.read(hdrs=hdrs) == data[-1000:], range_string)

        hdrs = {'Range': '0-4'}
        self.assert_(file_item.read(hdrs=hdrs) == data, range_string)

        # RFC 2616 14.35.1
        # "If the entity is shorter than the specified suffix-length, the
        # entire entity-body is used."
        range_string = 'bytes=-%d' % (file_length + 10)
        hdrs = {'Range': range_string}
        self.assert_(file_item.read(hdrs=hdrs) == data, range_string)

    def testRangedGetsWithLWSinHeader(self):
        #Skip this test until webob 1.2 can tolerate LWS in Range header.
        file_length = 10000
        file_item = self.env.container.file(Utils.create_name())
        data = file_item.write_random(file_length)

        for r in ('BYTES=0-999', 'bytes = 0-999', 'BYTES = 0 - 999',
                  'bytes = 0 - 999', 'bytes=0 - 999', 'bytes=0-999 '):

            self.assert_(file_item.read(hdrs={'Range': r}) == data[0:1000])

    def testFileSizeLimit(self):
        limit = load_constraint('max_file_size')
        tsecs = 3

        for i in (limit - 100, limit - 10, limit - 1, limit, limit + 1,
                  limit + 10, limit + 100):

            file_item = self.env.container.file(Utils.create_name())

            if i <= limit:
                self.assert_(timeout(tsecs, file_item.write,
                             cfg={'set_content_length': i}))
            else:
                self.assertRaises(ResponseError, timeout, tsecs,
                                  file_item.write,
                                  cfg={'set_content_length': i})

    def testNoContentLengthForPut(self):
        file_item = self.env.container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.write, 'testing',
                          cfg={'no_content_length': True})
        self.assert_status(411)

    def testDelete(self):
        file_item = self.env.container.file(Utils.create_name())
        file_item.write_random(self.env.file_size)

        self.assert_(file_item.name in self.env.container.files())
        self.assert_(file_item.delete())
        self.assert_(file_item.name not in self.env.container.files())

    def testBadHeaders(self):
        file_length = 100

        # no content type on puts should be ok
        file_item = self.env.container.file(Utils.create_name())
        file_item.write_random(file_length, cfg={'no_content_type': True})
        self.assert_status(201)

        # content length x
        self.assertRaises(ResponseError, file_item.write_random, file_length,
                          hdrs={'Content-Length': 'X'},
                          cfg={'no_content_length': True})
        self.assert_status(400)

        # bad request types
        #for req in ('LICK', 'GETorHEAD_base', 'container_info',
        #            'best_response'):
        for req in ('LICK', 'GETorHEAD_base'):
            self.env.account.conn.make_request(req)
            self.assert_status(405)

        # bad range headers
        self.assert_(len(file_item.read(hdrs={'Range': 'parsecs=8-12'})) ==
                     file_length)
        self.assert_status(200)

    def testMetadataLengthLimits(self):
        key_limit = load_constraint('max_meta_name_length')
        value_limit = load_constraint('max_meta_value_length')
        lengths = [[key_limit, value_limit], [key_limit, value_limit + 1],
                   [key_limit + 1, value_limit], [key_limit, 0],
                   [key_limit, value_limit * 10],
                   [key_limit * 10, value_limit]]

        for l in lengths:
            metadata = {'a' * l[0]: 'b' * l[1]}
            file_item = self.env.container.file(Utils.create_name())
            file_item.metadata = metadata

            if l[0] <= key_limit and l[1] <= value_limit:
                self.assert_(file_item.write())
                self.assert_status(201)
                self.assert_(file_item.sync_metadata())
            else:
                self.assertRaises(ResponseError, file_item.write)
                self.assert_status(400)
                file_item.metadata = {}
                self.assert_(file_item.write())
                self.assert_status(201)
                file_item.metadata = metadata
                self.assertRaises(ResponseError, file_item.sync_metadata)
                self.assert_status(400)

    def testEtagWayoff(self):
        file_item = self.env.container.file(Utils.create_name())
        hdrs = {'etag': 'reallylonganddefinitelynotavalidetagvalue'}
        self.assertRaises(ResponseError, file_item.write_random, hdrs=hdrs)
        self.assert_status(422)

    def testFileCreate(self):
        for i in range(10):
            file_item = self.env.container.file(Utils.create_name())
            data = file_item.write_random()
            self.assert_status(201)
            self.assert_(data == file_item.read())
            self.assert_status(200)

    def testHead(self):
        file_name = Utils.create_name()
        content_type = Utils.create_name()

        file_item = self.env.container.file(file_name)
        file_item.content_type = content_type
        file_item.write_random(self.env.file_size)

        md5 = file_item.md5

        file_item = self.env.container.file(file_name)
        info = file_item.info()

        self.assert_status(200)
        self.assertEquals(info['content_length'], self.env.file_size)
        self.assertEquals(info['etag'], md5)
        self.assertEquals(info['content_type'], content_type)
        self.assert_('last_modified' in info)

    def testDeleteOfFileThatDoesNotExist(self):
        # in container that exists
        file_item = self.env.container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.delete)
        self.assert_status(404)

        # in container that does not exist
        container = self.env.account.container(Utils.create_name())
        file_item = container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.delete)
        self.assert_status(404)

    def testHeadOnFileThatDoesNotExist(self):
        # in container that exists
        file_item = self.env.container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.info)
        self.assert_status(404)

        # in container that does not exist
        container = self.env.account.container(Utils.create_name())
        file_item = container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.info)
        self.assert_status(404)

    def testMetadataOnPost(self):
        file_item = self.env.container.file(Utils.create_name())
        file_item.write_random(self.env.file_size)

        for i in range(10):
            metadata = {}
            for j in range(10):
                metadata[Utils.create_ascii_name()] = Utils.create_name()

            file_item.metadata = metadata
            self.assert_(file_item.sync_metadata())
            self.assert_status((201, 202))

            file_item = self.env.container.file(file_item.name)
            self.assert_(file_item.initialize())
            self.assert_status(200)
            self.assertEquals(file_item.metadata, metadata)

    def testGetContentType(self):
        file_name = Utils.create_name()
        content_type = Utils.create_name()

        file_item = self.env.container.file(file_name)
        file_item.content_type = content_type
        file_item.write_random()

        file_item = self.env.container.file(file_name)
        file_item.read()

        self.assertEquals(content_type, file_item.content_type)

    def testGetOnFileThatDoesNotExist(self):
        # in container that exists
        file_item = self.env.container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.read)
        self.assert_status(404)

        # in container that does not exist
        container = self.env.account.container(Utils.create_name())
        file_item = container.file(Utils.create_name())
        self.assertRaises(ResponseError, file_item.read)
        self.assert_status(404)

    def testPostOnFileThatDoesNotExist(self):
        # in container that exists
        file_item = self.env.container.file(Utils.create_name())
        file_item.metadata['Field'] = 'Value'
        self.assertRaises(ResponseError, file_item.sync_metadata)
        self.assert_status(404)

        # in container that does not exist
        container = self.env.account.container(Utils.create_name())
        file_item = container.file(Utils.create_name())
        file_item.metadata['Field'] = 'Value'
        self.assertRaises(ResponseError, file_item.sync_metadata)
        self.assert_status(404)

    def testMetadataOnPut(self):
        for i in range(10):
            metadata = {}
            for j in range(10):
                metadata[Utils.create_ascii_name()] = Utils.create_name()

            file_item = self.env.container.file(Utils.create_name())
            file_item.metadata = metadata
            file_item.write_random(self.env.file_size)

            file_item = self.env.container.file(file_item.name)
            self.assert_(file_item.initialize())
            self.assert_status(200)
            self.assertEquals(file_item.metadata, metadata)

    def testSerialization(self):
        container = self.env.account.container(Utils.create_name())
        self.assert_(container.create())

        files = []
        for i in (0, 1, 10, 100, 1000, 10000):
            files.append({'name': Utils.create_name(),
                          'content_type': Utils.create_name(), 'bytes': i})

        write_time = time.time()
        for f in files:
            file_item = container.file(f['name'])
            file_item.content_type = f['content_type']
            file_item.write_random(f['bytes'])

            f['hash'] = file_item.md5
            f['json'] = False
            f['xml'] = False
        write_time = time.time() - write_time

        for format_type in ['json', 'xml']:
            for file_item in container.files(parms={'format': format_type}):
                found = False
                for f in files:
                    if f['name'] != file_item['name']:
                        continue

                    self.assertEquals(file_item['content_type'],
                                      f['content_type'])
                    self.assertEquals(int(file_item['bytes']), f['bytes'])

                    d = datetime.strptime(
                        file_item['last_modified'].split('.')[0],
                        "%Y-%m-%dT%H:%M:%S")
                    lm = time.mktime(d.timetuple())

                    if 'last_modified' in f:
                        self.assertEquals(f['last_modified'], lm)
                    else:
                        f['last_modified'] = lm

                    f[format_type] = True
                    found = True

                self.assert_(found, 'Unexpected file %s found in '
                             '%s listing' % (file_item['name'], format_type))

            headers = dict(self.env.conn.response.getheaders())
            if format_type == 'json':
                self.assertEquals(headers['content-type'],
                                  'application/json; charset=utf-8')
            elif format_type == 'xml':
                self.assertEquals(headers['content-type'],
                                  'application/xml; charset=utf-8')

        lm_diff = max([f['last_modified'] for f in files]) -\
            min([f['last_modified'] for f in files])
        self.assert_(lm_diff < write_time + 1, 'Diff in last '
                     'modified times should be less than time to write files')

        for f in files:
            for format_type in ['json', 'xml']:
                self.assert_(f[format_type], 'File %s not found in %s listing'
                             % (f['name'], format_type))

    def testStackedOverwrite(self):
        file_item = self.env.container.file(Utils.create_name())

        for i in range(1, 11):
            data = file_item.write_random(512)
            file_item.write(data)

        self.assert_(file_item.read() == data)

    def testTooLongName(self):
        file_item = self.env.container.file('x' * 1025)
        self.assertRaises(ResponseError, file_item.write)
        self.assert_status(400)

    def testZeroByteFile(self):
        file_item = self.env.container.file(Utils.create_name())

        self.assert_(file_item.write(''))
        self.assert_(file_item.name in self.env.container.files())
        self.assert_(file_item.read() == '')

    def testEtagResponse(self):
        file_item = self.env.container.file(Utils.create_name())

        data = StringIO.StringIO(file_item.write_random(512))
        etag = File.compute_md5sum(data)

        headers = dict(self.env.conn.response.getheaders())
        self.assert_('etag' in headers.keys())

        header_etag = headers['etag'].strip('"')
        self.assertEquals(etag, header_etag)

    def testChunkedPut(self):
        if (web_front_end == 'apache2'):
            raise SkipTest()
        data = File.random_data(10000)
        etag = File.compute_md5sum(data)

        for i in (1, 10, 100, 1000):
            file_item = self.env.container.file(Utils.create_name())

            for j in chunks(data, i):
                file_item.chunked_write(j)

            self.assert_(file_item.chunked_write())
            self.assert_(data == file_item.read())

            info = file_item.info()
            self.assertEquals(etag, info['etag'])


class TestFileUTF8(Base2, TestFile):
    set_up = False


class TestDloEnv(object):
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.container = cls.account.container(Utils.create_name())

        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        # avoid getting a prefix that stops halfway through an encoded
        # character
        prefix = Utils.create_name().decode("utf-8")[:10].encode("utf-8")
        cls.segment_prefix = prefix

        for letter in ('a', 'b', 'c', 'd', 'e'):
            file_item = cls.container.file("%s/seg_lower%s" % (prefix, letter))
            file_item.write(letter * 10)

            file_item = cls.container.file("%s/seg_upper%s" % (prefix, letter))
            file_item.write(letter.upper() * 10)

        man1 = cls.container.file("man1")
        man1.write('man1-contents',
                   hdrs={"X-Object-Manifest": "%s/%s/seg_lower" %
                         (cls.container.name, prefix)})

        man1 = cls.container.file("man2")
        man1.write('man2-contents',
                   hdrs={"X-Object-Manifest": "%s/%s/seg_upper" %
                         (cls.container.name, prefix)})

        manall = cls.container.file("manall")
        manall.write('manall-contents',
                     hdrs={"X-Object-Manifest": "%s/%s/seg" %
                           (cls.container.name, prefix)})


class TestDlo(Base):
    env = TestDloEnv
    set_up = False

    def test_get_manifest(self):
        file_item = self.env.container.file('man1')
        file_contents = file_item.read()
        self.assertEqual(
            file_contents,
            "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee")

        file_item = self.env.container.file('man2')
        file_contents = file_item.read()
        self.assertEqual(
            file_contents,
            "AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDDEEEEEEEEEE")

        file_item = self.env.container.file('manall')
        file_contents = file_item.read()
        self.assertEqual(
            file_contents,
            ("aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee" +
             "AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDDEEEEEEEEEE"))

    def test_get_manifest_document_itself(self):
        file_item = self.env.container.file('man1')
        file_contents = file_item.read(parms={'multipart-manifest': 'get'})
        self.assertEqual(file_contents, "man1-contents")

    def test_get_range(self):
        file_item = self.env.container.file('man1')
        file_contents = file_item.read(size=25, offset=8)
        self.assertEqual(file_contents, "aabbbbbbbbbbccccccccccddd")

        file_contents = file_item.read(size=1, offset=47)
        self.assertEqual(file_contents, "e")

    def test_get_range_out_of_range(self):
        file_item = self.env.container.file('man1')

        self.assertRaises(ResponseError, file_item.read, size=7, offset=50)
        self.assert_status(416)

    def test_copy(self):
        # Adding a new segment, copying the manifest, and then deleting the
        # segment proves that the new object is really the concatenated
        # segments and not just a manifest.
        f_segment = self.env.container.file("%s/seg_lowerf" %
                                            (self.env.segment_prefix))
        f_segment.write('ffffffffff')
        try:
            man1_item = self.env.container.file('man1')
            man1_item.copy(self.env.container.name, "copied-man1")
        finally:
            # try not to leave this around for other tests to stumble over
            f_segment.delete()

        file_item = self.env.container.file('copied-man1')
        file_contents = file_item.read()
        self.assertEqual(
            file_contents,
            "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffff")


class TestDloUTF8(Base2, TestDlo):
    set_up = False


class TestFileComparisonEnv:
    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()
        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.container = cls.account.container(Utils.create_name())

        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        cls.file_count = 20
        cls.file_size = 128
        cls.files = list()
        for x in range(cls.file_count):
            file_item = cls.container.file(Utils.create_name())
            file_item.write_random(cls.file_size)
            cls.files.append(file_item)

        cls.time_old = time.asctime(time.localtime(time.time() - 86400))
        cls.time_new = time.asctime(time.localtime(time.time() + 86400))


class TestFileComparison(Base):
    env = TestFileComparisonEnv
    set_up = False

    def testIfMatch(self):
        for file_item in self.env.files:
            hdrs = {'If-Match': file_item.md5}
            self.assert_(file_item.read(hdrs=hdrs))

            hdrs = {'If-Match': 'bogus'}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(412)

    def testIfNoneMatch(self):
        for file_item in self.env.files:
            hdrs = {'If-None-Match': 'bogus'}
            self.assert_(file_item.read(hdrs=hdrs))

            hdrs = {'If-None-Match': file_item.md5}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(304)

    def testIfModifiedSince(self):
        for file_item in self.env.files:
            hdrs = {'If-Modified-Since': self.env.time_old}
            self.assert_(file_item.read(hdrs=hdrs))

            hdrs = {'If-Modified-Since': self.env.time_new}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(304)

    def testIfUnmodifiedSince(self):
        for file_item in self.env.files:
            hdrs = {'If-Unmodified-Since': self.env.time_new}
            self.assert_(file_item.read(hdrs=hdrs))

            hdrs = {'If-Unmodified-Since': self.env.time_old}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(412)

    def testIfMatchAndUnmodified(self):
        for file_item in self.env.files:
            hdrs = {'If-Match': file_item.md5,
                    'If-Unmodified-Since': self.env.time_new}
            self.assert_(file_item.read(hdrs=hdrs))

            hdrs = {'If-Match': 'bogus',
                    'If-Unmodified-Since': self.env.time_new}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(412)

            hdrs = {'If-Match': file_item.md5,
                    'If-Unmodified-Since': self.env.time_old}
            self.assertRaises(ResponseError, file_item.read, hdrs=hdrs)
            self.assert_status(412)


class TestFileComparisonUTF8(Base2, TestFileComparison):
    set_up = False


class TestSloEnv(object):
    slo_enabled = None  # tri-state: None initially, then True/False

    @classmethod
    def setUp(cls):
        cls.conn = Connection(config)
        cls.conn.authenticate()

        if cls.slo_enabled is None:
            status = cls.conn.make_request('GET', '/info',
                                           cfg={'verbatim_path': True})
            if not (200 <= status <= 299):
                # Can't tell if SLO is enabled or not since we're running
                # against an old cluster, so let's skip the tests instead of
                # possibly having spurious failures.
                cls.slo_enabled = False
            else:
                # Don't bother looking for ValueError here. If something is
                # responding to a GET /info request with invalid JSON, then
                # the cluster is broken and a test failure will let us know.
                cluster_info = json.loads(cls.conn.response.read())
                cls.slo_enabled = 'slo' in cluster_info
            if not cls.slo_enabled:
                return

        cls.account = Account(cls.conn, config.get('account',
                                                   config['username']))
        cls.account.delete_containers()

        cls.container = cls.account.container(Utils.create_name())

        if not cls.container.create():
            raise ResponseError(cls.conn.response)

        seg_info = {}
        for letter, size in (('a', 1024 * 1024),
                             ('b', 1024 * 1024),
                             ('c', 1024 * 1024),
                             ('d', 1024 * 1024),
                             ('e', 1)):
            seg_name = "seg_%s" % letter
            file_item = cls.container.file(seg_name)
            file_item.write(letter * size)
            seg_info[seg_name] = {
                'size_bytes': size,
                'etag': file_item.md5,
                'path': '/%s/%s' % (cls.container.name, seg_name)}

        file_item = cls.container.file("manifest-abcde")
        file_item.write(
            json.dumps([seg_info['seg_a'], seg_info['seg_b'],
                        seg_info['seg_c'], seg_info['seg_d'],
                        seg_info['seg_e']]),
            parms={'multipart-manifest': 'put'})

        file_item = cls.container.file('manifest-cd')
        cd_json = json.dumps([seg_info['seg_c'], seg_info['seg_d']])
        file_item.write(cd_json, parms={'multipart-manifest': 'put'})
        cd_etag = hashlib.md5(seg_info['seg_c']['etag'] +
                              seg_info['seg_d']['etag']).hexdigest()

        file_item = cls.container.file("manifest-bcd-submanifest")
        file_item.write(
            json.dumps([seg_info['seg_b'],
                        {'etag': cd_etag,
                         'size_bytes': (seg_info['seg_c']['size_bytes'] +
                                        seg_info['seg_d']['size_bytes']),
                         'path': '/%s/%s' % (cls.container.name,
                                             'manifest-cd')}]),
            parms={'multipart-manifest': 'put'})
        bcd_submanifest_etag = hashlib.md5(
            seg_info['seg_b']['etag'] + cd_etag).hexdigest()

        file_item = cls.container.file("manifest-abcde-submanifest")
        file_item.write(
            json.dumps([
                seg_info['seg_a'],
                {'etag': bcd_submanifest_etag,
                 'size_bytes': (seg_info['seg_b']['size_bytes'] +
                                seg_info['seg_c']['size_bytes'] +
                                seg_info['seg_d']['size_bytes']),
                 'path': '/%s/%s' % (cls.container.name,
                                     'manifest-bcd-submanifest')},
                seg_info['seg_e']]),
            parms={'multipart-manifest': 'put'})


class TestSlo(Base):
    env = TestSloEnv
    set_up = False

    def setUp(self):
        super(TestSlo, self).setUp()
        if self.env.slo_enabled is False:
            raise SkipTest("SLO not enabled")
        elif self.env.slo_enabled is not True:
            # just some sanity checking
            raise Exception(
                "Expected slo_enabled to be True/False, got %r" %
                (self.env.slo_enabled,))

    def test_slo_get_simple_manifest(self):
        file_item = self.env.container.file('manifest-abcde')
        file_contents = file_item.read()
        self.assertEqual(4 * 1024 * 1024 + 1, len(file_contents))
        self.assertEqual('a', file_contents[0])
        self.assertEqual('a', file_contents[1024 * 1024 - 1])
        self.assertEqual('b', file_contents[1024 * 1024])
        self.assertEqual('d', file_contents[-2])
        self.assertEqual('e', file_contents[-1])

    def test_slo_get_nested_manifest(self):
        file_item = self.env.container.file('manifest-abcde-submanifest')
        file_contents = file_item.read()
        self.assertEqual(4 * 1024 * 1024 + 1, len(file_contents))
        self.assertEqual('a', file_contents[0])
        self.assertEqual('a', file_contents[1024 * 1024 - 1])
        self.assertEqual('b', file_contents[1024 * 1024])
        self.assertEqual('d', file_contents[-2])
        self.assertEqual('e', file_contents[-1])

    def test_slo_ranged_get(self):
        file_item = self.env.container.file('manifest-abcde')
        file_contents = file_item.read(size=1024 * 1024 + 2,
                                       offset=1024 * 1024 - 1)
        self.assertEqual('a', file_contents[0])
        self.assertEqual('b', file_contents[1])
        self.assertEqual('b', file_contents[-2])
        self.assertEqual('c', file_contents[-1])

    def test_slo_ranged_submanifest(self):
        file_item = self.env.container.file('manifest-abcde-submanifest')
        file_contents = file_item.read(size=1024 * 1024 + 2,
                                       offset=1024 * 1024 * 2 - 1)
        self.assertEqual('b', file_contents[0])
        self.assertEqual('c', file_contents[1])
        self.assertEqual('c', file_contents[-2])
        self.assertEqual('d', file_contents[-1])

    def test_slo_etag_is_hash_of_etags(self):
        expected_hash = hashlib.md5()
        expected_hash.update(hashlib.md5('a' * 1024 * 1024).hexdigest())
        expected_hash.update(hashlib.md5('b' * 1024 * 1024).hexdigest())
        expected_hash.update(hashlib.md5('c' * 1024 * 1024).hexdigest())
        expected_hash.update(hashlib.md5('d' * 1024 * 1024).hexdigest())
        expected_hash.update(hashlib.md5('e').hexdigest())
        expected_etag = expected_hash.hexdigest()

        file_item = self.env.container.file('manifest-abcde')
        self.assertEqual(expected_etag, file_item.info()['etag'])

    def test_slo_etag_is_hash_of_etags_submanifests(self):

        def hd(x):
            return hashlib.md5(x).hexdigest()

        expected_etag = hd(hd('a' * 1024 * 1024) +
                           hd(hd('b' * 1024 * 1024) +
                              hd(hd('c' * 1024 * 1024) +
                                 hd('d' * 1024 * 1024))) +
                           hd('e'))

        file_item = self.env.container.file('manifest-abcde-submanifest')
        self.assertEqual(expected_etag, file_item.info()['etag'])

    def test_slo_etag_mismatch(self):
        file_item = self.env.container.file("manifest-a-bad-etag")
        try:
            file_item.write(
                json.dumps([{
                    'size_bytes': 1024 * 1024,
                    'etag': 'not it',
                    'path': '/%s/%s' % (self.env.container.name, 'seg_a')}]),
                parms={'multipart-manifest': 'put'})
        except ResponseError as err:
            self.assertEqual(400, err.status)
        else:
            self.fail("Expected ResponseError but didn't get it")

    def test_slo_size_mismatch(self):
        file_item = self.env.container.file("manifest-a-bad-size")
        try:
            file_item.write(
                json.dumps([{
                    'size_bytes': 1024 * 1024 - 1,
                    'etag': hashlib.md5('a' * 1024 * 1024).hexdigest(),
                    'path': '/%s/%s' % (self.env.container.name, 'seg_a')}]),
                parms={'multipart-manifest': 'put'})
        except ResponseError as err:
            self.assertEqual(400, err.status)
        else:
            self.fail("Expected ResponseError but didn't get it")

    def test_slo_copy(self):
        file_item = self.env.container.file("manifest-abcde")
        file_item.copy(self.env.container.name, "copied-abcde")

        copied = self.env.container.file("copied-abcde")
        copied_contents = copied.read(parms={'multipart-manifest': 'get'})
        self.assertEqual(4 * 1024 * 1024 + 1, len(copied_contents))

    def test_slo_copy_the_manifest(self):
        file_item = self.env.container.file("manifest-abcde")
        file_item.copy(self.env.container.name, "copied-abcde",
                       parms={'multipart-manifest': 'get'})

        copied = self.env.container.file("copied-abcde")
        copied_contents = copied.read(parms={'multipart-manifest': 'get'})
        try:
            json.loads(copied_contents)
        except ValueError:
            self.fail("COPY didn't copy the manifest (invalid json on GET)")


class TestSloUTF8(Base2, TestSlo):
    set_up = False


if __name__ == '__main__':
    unittest.main()