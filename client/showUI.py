#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2013/12/30
# 用来处理主界面
from PyQt4 import QtGui, QtCore
from o_showUI import Ui_showWindow
from util import uploadFile, downloadFile, postPolicy

class MyShowWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_showWindow()
        self.ui.setupUi(self)
        
        self.filenames = [] # 上传文件名 格式为[[showfilename, realfilename, to, encrypted, audited ]]
        self.downFilenames = [] # 下载文件名
        self.count = 0 # 记录upload选中的个数
        self.count2 = 0 # 记录download选中的个数
        self.ui.frame.hide() # 设置upload底部状态栏不可见
        self.ui.frame2.hide() # 设置download底部状态栏不可见

        # [{filename :  , showname: , groupname: ,  container: , Auth Token: , StorageURL: , username: , policy: , encrypt: , audited: } ]   
        self.uploader = [] 
        
        self.downloader = [] 

        self.initQTable() # 初始化uploadTable
        
        QtCore.QObject.connect(self.ui.startButton, QtCore.SIGNAL('clicked()'), self.startEvent)
        QtCore.QObject.connect(self.ui.deleteButton, QtCore.SIGNAL('clicked()'), self.deleteEvent)
        QtCore.QObject.connect(self.ui.uploadTable, QtCore.SIGNAL('itemClicked(QTableWidgetItem *)'), self.uploadItemClicked)
#         QtCore.QObject.connect(self.ui.uploadTable, QtCore.SIGNAL('cellClicked(int, int)'), self.uploadCellClicked)
#         QtCore.QObject.connect(self.ui.checkBox, QtCore.SIGNAL('stateChanged(int)'), self.chooseAll)
        QtCore.QObject.connect(self.ui.checkBox, QtCore.SIGNAL('clicked()'), self.chooseAll)
        QtCore.QObject.connect(self.ui.encryptCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.encrypt)
        QtCore.QObject.connect(self.ui.auditCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.audit)
        
        # download tab signal
        QtCore.QObject.connect(self.ui.startButton2, QtCore.SIGNAL('clicked()'), self.startEvent2)
        QtCore.QObject.connect(self.ui.deleteButton2, QtCore.SIGNAL('clicked()'), self.deleteEvent2)
#         QtCore.QObject.connect(self.ui.checkBox2, QtCore.SIGNAL('stateChanged(int)'), self.chooseAll2)
        QtCore.QObject.connect(self.ui.checkBox2, QtCore.SIGNAL('clicked()'), self.chooseAll2)
        QtCore.QObject.connect(self.ui.downloadTable, QtCore.SIGNAL('itemClicked(QTableWidgetItem *)'), self.downloadItemClicked)
        
    
    def setUserInfo(self, result):
        import copy
        self.userInfo = copy.deepcopy(result)
        print 'showUI the userInfo is:'
        print self.userInfo
        
    def showFrame(self):
        '''
        show the upload bottom frame
        '''
        if self.count != 0:
            self.ui.frame.show()
            self.ui.checkBox.setText(str(self.count)+'selected')
            if self.count == len(self.filenames):
                self.ui.checkBox.setChecked(True)
            else:
                self.ui.checkBox.setChecked(False)
        else:
            self.ui.frame.hide()
   
    def showFrame2(self):
        '''
        show the download bottom frame
        '''
        if self.count2 != 0:
            self.ui.frame2.show()
            self.ui.checkBox2.setText(str(self.count2) + 'selected')
            if self.count2 == len(self.downFilenames):
                self.ui.checkBox2.setChecked(True)
            else:
                self.ui.checkBox2.setChecked(False)
        else:
            self.ui.frame2.hide()
        
    def initQTable(self):
        '''
        初始化uploadTable, downloadTable，设置一些基本的显示模式
        '''
        # 表项不可修改
        self.ui.uploadTable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.ui.downloadTable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        # 最后一列拉伸
        self.ui.uploadTable.horizontalHeader().setStretchLastSection(True)
        self.ui.downloadTable.horizontalHeader().setStretchLastSection(True)
        # 设置整行选择
        self.ui.uploadTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.downloadTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # 设置第一列的宽度
        self.ui.uploadTable.setColumnWidth(0, 23)
        self.ui.uploadTable.setColumnWidth(1, 160)
        self.ui.uploadTable.setColumnWidth(2, 80)
        self.ui.uploadTable.setColumnWidth(3, 50)
        self.ui.uploadTable.setColumnWidth(4, 50)
        
        self.ui.downloadTable.setColumnWidth(0, 23)
        self.ui.downloadTable.setColumnWidth(1, 180)
        self.ui.downloadTable.setColumnWidth(2, 80)
        self.ui.downloadTable.setColumnWidth(3, 80)
        # 设置隔行颜色不同
        self.ui.uploadTable.setAlternatingRowColors(True)
        self.ui.downloadTable.setAlternatingRowColors(True)
        # 不显示网格线
        self.ui.uploadTable.setShowGrid(False)
        self.ui.downloadTable.setShowGrid(False)
        
        # 添加水平表头
        self.ui.uploadTable.setHorizontalHeaderLabels([u' ','filename','progress','enc', 'audit', 'to'])
        # 设置表头格式
        for n in range(self.ui.uploadTable.columnCount()):
            headItem = self.ui.uploadTable.horizontalHeaderItem(n)
            headItem.setTextAlignment(0x0001 | 0x0080)  # 设置表头内容居中靠左 QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter
            headItem.setFont(QtGui.QFont("Helvetica"))
            headItem.setBackgroundColor(QtGui.QColor(0,68,10))
            headItem.setTextColor(QtGui.QColor(200,111,30))    
        
        self.ui.downloadTable.setHorizontalHeaderLabels([u' ','filename','progress','state', 'from'])
        # 设置表头格式
        for n in range(self.ui.downloadTable.columnCount()):
            headItem = self.ui.downloadTable.horizontalHeaderItem(n)
            headItem.setTextAlignment(0x0001 | 0x0080)  # 设置表头内容居中靠左 QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter
            headItem.setFont(QtGui.QFont("Helvetica"))
            headItem.setBackgroundColor(QtGui.QColor(0,68,10))
            headItem.setTextColor(QtGui.QColor(200,111,30)) 
   
    def uploadItemClicked(self, item):
        row = item.row()
        column = item.column()
        if column != 0:
            if self.ui.uploadTable.item(row,0).checkState() == QtCore.Qt.Checked:
                self.ui.uploadTable.item(row,0).setCheckState(QtCore.Qt.Unchecked)
                self.count = self.count - 1
            else:
                self.ui.uploadTable.item(row, 0).setCheckState(QtCore.Qt.Checked)
                self.count = self.count + 1
        else:
            if self.ui.uploadTable.item(row,0).checkState() == QtCore.Qt.Checked:
                self.count = self.count + 1
            else:
                self.count = self.count - 1
         
        self.showFrame()
    
    
    def startEvent(self):
        '''
        start/stop upload
        应该使用多线程方式实现
        ''' 
        for i in range(self.ui.uploadTable.rowCount()):
            if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                if 'encrypt' not in self.uploader[i]:
                    self.uploader[i]['encrypt'] = 'N'
                if 'audit' not in self.uploader[i]:
                    self.uploader[i]['audit'] = 'N'
                uploadFile(self.uploader[i])                
                if 'policy' in str(self.uploader[i]) and self.uploader[i]['policy'].strip() != '':
                    print '.........',  self.uploader
                    print 'post policy'
                    postPolicy(self.uploader[i])
                    self.parentWidget().freshGroupTable()
                else:
                    self.parentWidget().freshEvent()
                self.ui.uploadTable.item(i, 2).setText('Succeed')
        

    
    def deleteEvent(self):
        '''
        delete upload
        '''
        print 'delete'
        for i in range(self.ui.uploadTable.rowCount() - 1, -1, -1):
            if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:   
                self.ui.uploadTable.removeRow(i) # 删掉选中的表项
                del self.uploader[i]
                self.count = self.count - 1
       
        self.showFrame()
        print repr(self.filenames)
        

    def setUploader(self, fileInfo):
        print 'The fileInfo is >>>>>>', fileInfo
        print 'the uploader >>>>>>', self.uploader
        
        if fileInfo in self.uploader:
            print "already in the show window"
            return

        name = fileInfo['filename']
        fileInfo['filename'] = name[name.find("'")+1 : name.rfind("'")]
        fileInfo['showname'] = name[name.rfind("/") + 1 : name.rfind("'")]
        self.uploader.append(fileInfo)
        
        row = self.ui.uploadTable.rowCount()
        self.ui.uploadTable.setRowCount(row + 1) # 新增加一行
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.count += 1
        self.ui.uploadTable.setItem(row, 0, item)   # 添加复选框
                
        item = QtGui.QTableWidgetItem(fileInfo['showname'])
        self.ui.uploadTable.setItem(row, 1, item)   # 显示filename
        
        item = QtGui.QTableWidgetItem('waited')
        self.ui.uploadTable.setItem(row, 2, item)   # 显示progress
            
        item = QtGui.QTableWidgetItem(' ')
        self.ui.uploadTable.setItem(row, 3, item)   # 显示enc
            
        item = QtGui.QTableWidgetItem(' ')
        self.ui.uploadTable.setItem(row, 4, item)   # 显示audit
                
        item = QtGui.QTableWidgetItem(fileInfo['container'])
        self.ui.uploadTable.setItem(row, 5, item)   # 显示to
        
        self.showFrame()
    
        
    def freshUploadTable(self):
        '''
         更新uploadTable中的显示
        '''
        row = len(self.uploader)
        self.ui.uploadTable.setRowCount(row)
        for i in range (row):
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.uploadTable.setItem(row, 0, item)   # 添加复选框
                    
            item = QtGui.QTableWidgetItem(self.uploader[i]['showname'])
            self.ui.uploadTable.setItem(row, 1, item)   # 显示filename
            
            item = QtGui.QTableWidgetItem('waited')
            self.ui.uploadTable.setItem(row, 2, item)   # 显示progress
                
            item = QtGui.QTableWidgetItem(' ')
            self.ui.uploadTable.setItem(row, 3, item)   # 显示enc
                
            item = QtGui.QTableWidgetItem(' ')
            self.ui.uploadTable.setItem(row, 4, item)   # 显示audit
                
            item = QtGui.QTableWidgetItem(self.uploader[i]['container'])
            self.ui.uploadTable.setItem(row, 5, item)   # 显示to
        

    def chooseAll(self):
        '''
        复选框全选/或全部取消
        '''
        if self.ui.checkBox.checkState() == QtCore.Qt.Checked:  # 选中状态
            self.count = self.ui.uploadTable.rowCount()
            self.ui.checkBox.setText(str(self.count) + ' selected')
            for i in range(self.count):
                self.ui.uploadTable.item(i, 0).setCheckState(QtCore.Qt.Checked)
        else:
            self.count = 0
            self.ui.frame.hide()
            for i in range(self.ui.uploadTable.rowCount()):
                self.ui.uploadTable.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
 
 
    def encrypt(self):
        '''
        是否加密上传
        '''
        if self.ui.encryptCheckBox.isChecked():
            for i in range(self.ui.uploadTable.rowCount()):
                if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                    self.ui.uploadTable.item(i, 3).setText('E')   # 显示filename
                    self.uploader[i]['encrypt'] = 'E'
        else:
            for i in range(self.ui.uploadTable.rowCount()):
                if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                    self.ui.uploadTable.item(i, 3).setText(' ')
                    self.uploader[i]['encrypt'] = 'N'
 
                    
    def audit(self):
        '''
        是否审计
        '''
        if self.ui.auditCheckBox.isChecked():
            for i in range(self.ui.uploadTable.rowCount()):
                if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                    self.ui.uploadTable.item(i, 4).setText('A')   # 显示filename
                    self.uploader[i]['audit'] = 'A'
        else:
            for i in range(self.ui.uploadTable.rowCount()):
                if self.ui.uploadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                    self.ui.uploadTable.item(i, 4).setText(' ')
                    self.uploader[i]['audit'] = 'N'
                    
  
######################################################################################
    def setDownloadFilenames(self, files):
        index = len(self.downloader)
        self.ui.downloadTable.setRowCount(index)
        for name in files:
            if name not in self.downloader:
                self.downloader.append(name)
                self.ui.downloadTable.setRowCount(len(self.downloader))
                
                item = QtGui.QTableWidgetItem()
                item.setCheckState(QtCore.Qt.Checked)
                self.count2 += 1
                self.ui.downloadTable.setItem(index, 0, item)   # 添加复选框
                
                item = QtGui.QTableWidgetItem(name['filename'])
                self.ui.downloadTable.setItem(index, 1, item)   # 显示文件名
                
                item = QtGui.QTableWidgetItem(' ')
                self.ui.downloadTable.setItem(index, 2, item)   # 显示速度
                
                item = QtGui.QTableWidgetItem('waiting')
                self.ui.downloadTable.setItem(index, 3, item)   # 显示状态
                
                item = QtGui.QTableWidgetItem(name['group'])
                self.ui.downloadTable.setItem(index, 4, item)   # 显示状态
                
                index = index + 1
        
        self.showFrame2()
        
    
    def startEvent2(self):
        for i in range(self.ui.downloadTable.rowCount()):
            if self.ui.downloadTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                ans = downloadFile(self.downloader[i]['filename'], self.downloader[i]['Auth Token'], self.downloader[i]['StorageURL'], self.downloader[i]['container'])
                print 'ans' , ans
                if ans != 'forbidden':
                    self.ui.downloadTable.item(i, 3).setText('succeed')
                else :
                    QtGui.QMessageBox.information(self, 'Info', 'Sorry, you have no privieledge to download:\n\t' + self.downloader[i]['filename'],  QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    self.ui.downloadTable.item(i, 3).setText('denied')
    
    
    def deleteEvent2(self):
        '''
        delete the selected download item
        '''
        for i in range(self.ui.downloadTable.rowCount() - 1, -1, -1):
            if self.ui.downloadTable.item(i, 0).checkState() == QtCore.Qt.Checked:   
                self.ui.downloadTable.removeRow(i) # 删掉选中的表项
                del self.downloader[i]
                self.count2 = self.count2 - 1
       
        self.showFrame2()
        print repr(self.downFilenames)
        
    
    def chooseAll2(self):
        '''
        choose all the item to download
        '''
        if self.ui.checkBox2.checkState() == QtCore.Qt.Checked:  # 选中状态
            self.count2 = self.ui.downloadTable.rowCount()
            self.ui.checkBox2.setText(str(self.count2) + ' selected')
            for i in range(self.count2):
                self.ui.downloadTable.item(i, 0).setCheckState(QtCore.Qt.Checked)
        else:
            self.count2 = 0
            self.ui.frame2.hide()
            for i in range(self.ui.downloadTable.rowCount()):
                self.ui.downloadTable.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
        
  
    def downloadItemClicked(self, item):
        '''
        downloadTable 的某一行被选中，将更改改行的选中状态
        '''
        row = item.row()
        column = item.column()
        if column  != 0:            
            if self.ui.downloadTable.item(row, 0).checkState() == QtCore.Qt.Checked:
                self.ui.downloadTable.item(row, 0).setCheckState(QtCore.Qt.Unchecked)
                self.count2 = self.count2 - 1
            else:
                self.ui.downloadTable.item(row, 0).setCheckState(QtCore.Qt.Checked)
                self.count2 = self.count2 + 1
        else:
            if self.ui.downloadTable.item(row, 0).checkState() == QtCore.Qt.Checked:
                self.count2 = self.count2 + 1
            else:
                self.count2 = self.count2 - 1
        
        self.showFrame2()        