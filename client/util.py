#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2013/1/4
# 各种工具，用来处理加解密上传\下载,审计相关
import os

from encrypt import aesEncrypt
import swauthlist
import swift_test as swift


key = '1234567887654321'
aes = aesEncrypt(key)

def qToString(name):
    return name[name.find("'")+1 : name.rfind("'")]

def readFile(filename):
    f = open(filename, 'rb')
    result = f.read()
    f.close()
    return result

def writeFile(filename, content):
    f = open(filename, 'wb')
    f.write(content)
    f.close()

def groupInfo( groupname, username):
    command = ['-A', 'http://127.0.0.1:8080/auth/', '-U', groupname + ':' + username, '-K', username,  groupname]
    return swauthlist.opt(command)

def listObject(authToken, storageUrl, username):
    command = ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'list', username, '--lh']
    return swift.opt(command)

def addContainer(authToken, storageUrl, container):
    command =  ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'post', container]
    return swift.opt(command)

def deleteContainer(authToken, storageUrl, container):
    command =  ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'delete', container]
    return swift.opt(command)

def listContainer(authToken, storageUrl):
    command =  ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'list']
    return swift.opt(command)

def postPolicy(uploader):
    command = ['--os-auth-token', uploader['Auth Token'], '--os-storage-url', uploader['StorageURL'], 'post',uploader['container']]
    if 'E'  == uploader['encrypt']: # 加密上传
        command.append(uploader['showname']+'_E')
    else:
        command.append(uploader['showname'])
        
    command.append('-m')
    command.append('attr_policy:' + uploader['policy'])
    print '>>>>>>>>>>>', command
    swift.opt(command) 

def uploadFile(uploaders):
    # command = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','upload', 'wzb']
    # filename == [realname, showname, to(容器名), enc, audit]
    command = ['--os-auth-token', uploaders['Auth Token'], '--os-storage-url', uploaders['StorageURL'], 'upload',uploaders['container']]
    if 'E'  == uploaders['encrypt']: # 加密上传
        writeFile(uploaders['showname']+'_E', aes.encrypt(readFile(str(uploaders['filename'])))) 
        command.append(uploaders['showname']+'_E')
        swift.opt(command)
        os.remove(uploaders['showname']+'_E')
    else:
        writeFile(uploaders['showname'], readFile(str(uploaders['filename'])))
        command.append(uploaders['showname'])
        swift.opt(command)
        os.remove(uploaders['showname'])

        
def downloadFile(filename, authToken, storageUrl, container):
    print 'start to download : ', str(filename)
#     command = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','download', 'wzb']
    command = ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'download', container]
    command.extend([str(filename), '-o', '/home/wzb/datamodel/download/' + str(filename)])
    rs = swift.opt(command)
    if rs == 'error':
        print rs,  'wuzebang'
        return 'forbidden'
    if not os.path.exists('/home/wzb/datamodel/download/' + str(filename)) :
        return 'forbidden'
    
    files = str(filename).split('_')
    print repr(files)
    if 'E' in files:
        writeFile('/home/wzb/datamodel/download/' + files[0], aes.decrypt(readFile('/home/wzb/datamodel/download/' + str(filename))))
        os.remove('/home/wzb/datamodel/download/' + str(filename))
    
    return 'succeed'