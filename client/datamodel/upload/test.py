#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2013/1/4
# 各种工具，用来处理加解密上传\下载,审计相关
import swift_test as swift
from encrypt import aesEncrypt
import os

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

def uploadFile(filename, authToken, storageUrl):
    # command = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','upload', 'wzb']
    # filename == [realname, showname, to(容器名), enc, audit]
    command = ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'upload', filename[2]]  #  filename[2] 为容器名
    if 'E' in filename: # 加密上传
        writeFile(filename[1]+'_E', aes.encrypt(readFile(filename[0]))) 
        command.append(filename[1]+'_E')
        swift.opt(command)
        os.remove(filename[1]+'_E')
    else:
        writeFile(filename[1], readFile(filename[0]))
        command.append(filename[1])
        swift.opt(command)
        os.remove(filename[1])

# def uploadFiles(filenames):
#     for filename in filenames:
#         uploadFile(filename)    
        
def downloadFile(filename, authToken, storageUrl, username):
    print 'start to download : ', str(filename)
#     command = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','download', 'wzb']
    command = ['--os-auth-token', authToken, '--os-storage-url', storageUrl, 'download', username]
    command.extend([str(filename), '-o', '/home/wzb/datamodel/download/' + str(filename)])
    swift.opt(command)
    
    files = str(filename).split('_')
    print repr(files)
    if 'E' in files:
        writeFile('/home/wzb/datamodel/download/' + files[0], aes.decrypt(readFile('/home/wzb/datamodel/download/' + str(filename))))
        os.remove('/home/wzb/datamodel/download/' + str(filename))