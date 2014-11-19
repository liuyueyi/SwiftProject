#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2013/12/31
# aes 加密解密封装类

from Crypto.Cipher import AES

class aesEncrypt():
    def __init__(self,key):
        self.key = key
        self.mode = AES.MODE_CBC #plaintext length (in bytes) must be a multiple of block_size
        self.iv = '1234567887654321' # ase key iv 
        
    def encrypt(self,text):
        cryptor = AES.new(self.key,self.mode,self.iv)
        length = 16
        count = text.count('')
        if count < length:
            add = (length-count) + 1
            text = text + (' ' * add)
        elif count > length:
            add = (length-(count % length)) + 1
            text = text + (' ' * add)
        self.ciphertext = cryptor.encrypt(text)
        return self.ciphertext
    
    def decrypt(self,text):
        cryptor = AES.new(self.key,self.mode,self.iv)
        plain_text  = cryptor.decrypt(text)
        return plain_text.rstrip()
