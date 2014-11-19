#!/usr/bin/env python 
## This file is created by wuzbeang 2013/12/26
## used to test how to use client function
import mock
import httplib
import logging
import socket
import StringIO
# import testtools
import warnings
from urlparse import urlparse

# TODO: mock http connection class with more control over headers
from .utils import fake_http_connect, fake_get_keystoneclient_2_0
from swiftclient import client as c

def test_ok(self):
    c.http_connection = self.fake_http_connection(200)
    url, token = c.get_auth('httpL//127.0.0.1:8080', 'tester', 'testing')
    self.assertEqual(url, None)
    self.assertEqual(token, None)
    
if __name__=='__main__':
    test_ok()
    print "over!"