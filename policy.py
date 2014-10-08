#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2014/3/4
# 
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignature

class Ui_policyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        uic.loadUi("policyUI.ui", self)
        
        QtCore.QObject.connect(self.andButton, QtCore.SIGNAL('clicked()'), self.andButtonClicked)
        QtCore.QObject.connect(self.orButton, QtCore.SIGNAL('clicked()'), self.orButtonClicked)
        QtCore.QObject.connect(self.notButton, QtCore.SIGNAL('clicked()'), self.notButtonClicked)
        QtCore.QObject.connect(self.leftBracketButton, QtCore.SIGNAL('clicked()'), self.leftBracketButtonClicked)
        QtCore.QObject.connect(self.rightBracketButton, QtCore.SIGNAL('clicked()'), self.rigthtBracketButtonClicked)
        QtCore.QObject.connect(self.clearButton, QtCore.SIGNAL('clicked()'), self.clearButtonClicked)
        QtCore.QObject.connect(self.sureButton, QtCore.SIGNAL('clicked()'), self.sureButtonClicked)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancelButtonClicked)
        
        QtCore.QObject.connect(self.attributeList, QtCore.SIGNAL('itemClicked(QListWidgetItem *)'), self.listItemClicked)
        
    def initAttributeList(self, attrs):
        self.attributeList.clear()
        for attr in attrs:
            self.attributeList.addItem(attr)
            
    def andButtonClicked(self):
        self.policyEdit.setText(str(self.policyEdit.text()) + ' and')
    
    def orButtonClicked(self):
        self.policyEdit.setText(str(self.policyEdit.text()) + ' or')
        
    def notButtonClicked(self):
        self.policyEdit.setText(str(self.policyEdit.text()) + ' not')
        
    def leftBracketButtonClicked(self):
        self.policyEdit.setText(str(self.policyEdit.text()) + '(')
        
    def rigthtBracketButtonClicked(self):
        self.policyEdit.setText(str(self.policyEdit.text()) + ')')
        
    def clearButtonClicked(self):
        self.policyEdit.setText('')
    
    def listItemClicked(self, item):
        self.policyEdit.setText(str(self.policyEdit.text()) + ' ' +  item.text())
    
    def cancelButtonClicked(self):
        self.emit(QtCore.SIGNAL('cancel(QString)'), 'cancel')
        self.close()
    
    def sureButtonClicked(self):
        policy  = str(self.policyEdit.text()).strip()
        print '...........' , policy
        self.emit(QtCore.SIGNAL('sure(QString)'), policy)
        self.close()
