#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2013/12/30
# 用来处理主界面

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QTableWidget
from urllib import unquote

from o_mainUI import Ui_Form
from policy import Ui_policyDialog
from showUI import MyShowWindow
import swift_test as swift
import util


#from util import listObject, listContainer
# import my file
class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # 窗体居中显示，且大小不可变
        self.setFixedSize(829,752)
        width = QtGui.QApplication.desktop().width() - 829
        height = QtGui.QApplication.desktop().height() - 752
        self.move(width/2, height/2)
        
        # 获得UI对象
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        
        #####
        # 个人空间信息
        self. containerName = None  # 当前的container name
        self.ui.containerNameEdit.hide() # 设置新建目录名输入窗口隐藏
        
        self.ui.containerList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)   #定义右键菜单
        #self.ui.containerList.customContextMenuRequested.connect(self.on_containerList_customContextMenuRequested)
        
        # 获得上传下载界面，并隐藏
        self.showUI = MyShowWindow(self)
        self.showUI.hide()
        
        self.ui.frame.hide()
        self.count = 0  # 记录选中的个数
        self.initQTable()   # 初始化私人空间tableWidget
        ##
        ######
        
        ## 初始化组空间
        self.userInfo = {}
        self.count2 = 0
        self.policyDialog = Ui_policyDialog()
        self.ui.lineEdit.hide() # 隐藏用来搜索组名，或者增加容器的lineEdit
        self.initGroup()    # 初始化用来显示object的table
        self.ui.groupTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # 定义groupTree的右键菜单
        
        self.groupInfo = {}     # 用户所有组信息, 形容： {  group1: { 'StorageURL' :  url,  'Auth Token' : token,  'Owner' : owner} }
        self.groupContainers = {} # 用户组内所有容器 : { group1: [container1, container2] }
        self.currentGroup = None
        self.currentGroupContainer = None 
        self.uploadFile = {}    # {filename :  , showname: , groupname: ,  container: , Auth Token: , StorageURL: , username: , policy:}   
        
        self.downloadFiles = []
        # 绑定信号槽
        QtCore.QObject.connect(self.ui.uploadButton, QtCore.SIGNAL('clicked()'), self.uploadEvent)
        QtCore.QObject.connect(self.ui.showButton, QtCore.SIGNAL('clicked()'), self.showInfoWindow)
        QtCore.QObject.connect(self.ui.downloadButton, QtCore.SIGNAL('clicked()'), self.downloadEvent)
        QtCore.QObject.connect(self.ui.deleteButton, QtCore.SIGNAL('clicked()'), self.deleteEvent)
        QtCore.QObject.connect(self.ui.freshButton, QtCore.SIGNAL('clicked()'), self.freshEvent)
        QtCore.QObject.connect(self.ui.infoTable, QtCore.SIGNAL('itemClicked(QTableWidgetItem *)'), self.infoTableItemClicked)
        QtCore.QObject.connect(self.ui.checkBox, QtCore.SIGNAL('clicked()'), self.chooseAll)
        QtCore.QObject.connect(self.ui.containerList, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.containerListItemClicked)
        QtCore.QObject.connect(self.ui.addButton, QtCore.SIGNAL('clicked()'), self.addContainerEvent)
        
        QtCore.QObject.connect(self.ui.groupTree, QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'), self.groupTreeItemClicked)
        QtCore.QObject.connect(self.ui.groupTable, QtCore.SIGNAL('itemClicked(QTableWidgetItem *)'), self.groupTableItemClicked)
        QtCore.QObject.connect(self.ui.checkBox2, QtCore.SIGNAL('clicked()'), self.chooseAll2)
        QtCore.QObject.connect(self.ui.searchButton, QtCore.SIGNAL('clicked()'), self.searchEvent)
        QtCore.QObject.connect(self.ui.downloadButton2, QtCore.SIGNAL('clicked()'), self.downloadEvent2)
        QtCore.QObject.connect(self.ui.deleteButton2, QtCore.SIGNAL('clicked()'), self.deleteEvent2)
        
        QtCore.QObject.connect(self.policyDialog, QtCore.SIGNAL('sure(QString)'),  self.sureEvent)
        QtCore.QObject.connect(self.policyDialog, QtCore.SIGNAL('cancel(QString)'),  self.cancelEvent)
        
    ########################
    #激活菜单事件
    @pyqtSignature("QPoint")
    def on_containerList_customContextMenuRequested(self, point):
        item = self.ui.containerList.itemAt(point)
#         row = self.ui.containerList.currentRow()
        #空白区域不显示菜单
        if item != None:
            self.rightMenuShow()

    #创建右键菜单
    def rightMenuShow(self):
        rightMenu = QtGui.QMenu(self.ui.containerList)
        showAction = QtGui.QAction("show", self, triggered=self.showItem)       
        rightMenu.addAction(showAction)
        
        removeAction = QtGui.QAction("delete", self, triggered=self.deleteItem)       
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
    
    def showItem(self):
        '''
        显示该容器下的所有对象
        '''
        item = self.ui.containerList.currentItem()
        self.containerListItemClicked(item)
        
    
    def deleteItem(self):
        '''
        删除容器
        '''
        delName = util.qToString(repr(self.ui.containerList.currentItem().text()))
        util.deleteContainer(self.userInfo['Auth Token'], self.userInfo['StorageURL'], delName )
        if delName == self.containerName:
            self.containerName = 'fill'
            self.freshEvent()
        else:
            self.ui.containerList.takeItem(self.ui.containerList.currentRow())
    ######################
    
    def setUserInfo(self, result):
        self.userInfo = result
        self.showUI.setUserInfo(result)
        self.setWindowTitle('welcome, ' +result['username'])
        self.initTree()     # 显示所有的组
        del result
    
    def showFrame(self):
        '''
        show the bottom frame
        '''
        if self.count != 0:
            self.ui.frame.show()
            self.ui.checkBox.setText(str(self.count)+'selected')
            if self.count == self.ui.infoTable.rowCount():
                self.ui.checkBox.setChecked(True)
            else:
                self.ui.checkBox.setChecked(False)
        else:
            self.ui.frame.hide()
    
    
    def freshEvent(self):
        '''
        刷新列表
        '''
#         content = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','list', 'wzb', '--lh']
#         result = swift.opt(content)
#         if result != None:
#             self.count = 0
#             self.updateQTable(result)
        result = util.listContainer(self.userInfo['Auth Token'], self.userInfo['StorageURL'])
        print '>>>>>>>>>', result
        if result != []:
            self.initContainerList(result)
        else:   # 没有容器则退出
            return
                
        if self.containerName == None:
            self.containerName = result[0]['name']
        result = util.listObject(self.userInfo['Auth Token'], self.userInfo['StorageURL'], self.containerName)
        if result != None:
            self.count = 0
            self.updateQTable(result)
                
        
    def initQTable(self):
        '''
        初始化QTableWidget，设置一些基本的显示模式
        '''
        # 表项不可修改
        self.ui.infoTable.setEditTriggers(QTableWidget.NoEditTriggers)
        # 最后一列拉伸
        self.ui.infoTable.horizontalHeader().setStretchLastSection(True)
        # 设置整行选择
        self.ui.infoTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # 设置第一列的宽度
        self.ui.infoTable.setColumnWidth(0, 23)
        self.ui.infoTable.setColumnWidth(1, 300)
        self.ui.infoTable.setColumnWidth(2, 120)
        # 设置隔行颜色不同
        self.ui.infoTable.setAlternatingRowColors(True)
        # 不显示网格线
        self.ui.infoTable.setShowGrid(False)
        
        # 添加水平表头
        self.ui.infoTable.setHorizontalHeaderLabels([u' ','filename','size','lastModified'])
        # 设置表头格式
        for n in range(self.ui.infoTable.columnCount()):
            headItem = self.ui.infoTable.horizontalHeaderItem(n)
            headItem.setTextAlignment(0x0001 | 0x0080)  # 设置表头内容居中靠左 QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter
            headItem.setFont(QtGui.QFont("Helvetica"))
            headItem.setBackgroundColor(QtGui.QColor(0,68,10))
            headItem.setTextColor(QtGui.QColor(200,111,30))            
        
        
    def initContainerList(self, result):
        '''
        初始化ContainerList, 获得用户容器
        '''
        size = len(result)
        self.ui.containerList.clear()
        for i in range(0, size):        
            self.ui.containerList.addItem(result[i]['name'])
            self.ui.containerList.item(i).setIcon(QtGui.QIcon("res/container.png"))
         
        
    def updateQTable(self, result):
        '''
        根据从云端获得的列表，更新显示
        '''
        count = len(result)
        self.ui.infoTable.setRowCount(count)
        for i in range(0, count):
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.infoTable.setItem(i, 0, item)   # 添加复选框
            
            item = QtGui.QTableWidgetItem(result[i]['name'])
            self.ui.infoTable.setItem(i, 1, item)
            
            item = QtGui.QTableWidgetItem()
            size = result[i]['byte_str']
            if 'G' not in size and 'M' not in size or 'K' not in size  or 'B' not in size:
                size = size + 'b'
            item.setText(size)
            self.ui.infoTable.setItem(i, 2, item)
            
            item = QtGui.QTableWidgetItem(result[i]['date'])
            self.ui.infoTable.setItem(i, 3, item)
    
    
    def containerListItemClicked(self, item):
        '''
        '''
        self.count = 0 #  选中对象个数初始化为0
        self.showFrame() # 不显示底部窗体 
        
        name = repr(item.text())
        self.containerName = name[name.find("'")+1 : name.rfind("'")]
        print 'The selected container is : ',repr(self.containerName)
        result = util.listObject(self.userInfo['Auth Token'], self.userInfo['StorageURL'], self.containerName)
        self.updateQTable(result)
          
            
    def infoTableItemClicked(self,item):
        """
        item复选框选中触发事件
        """
        row = item.row()
        column = item.column()
        if column != 0:
            if self.ui.infoTable.item(row,0).checkState() == QtCore.Qt.Checked:            
                self.ui.infoTable.item(row,0).setCheckState(QtCore.Qt.Unchecked)
                self.count = self.count - 1
            else:            
                self.ui.infoTable.item(row, 0).setCheckState(QtCore.Qt.Checked)
                self.count = self.count + 1
        else:
            if self.ui.infoTable.item(row,0).checkState() == QtCore.Qt.Checked:       
                self.count = self.count + 1
            else:                  
                self.count = self.count - 1
                
        self.showFrame()
        
        
    def showInfoWindow(self):
        '''
        显示上传下载界面
        '''
        if self.showUI != None:
            self.showUI.show()
        else:
            self.showUI = MyShowWindow(self)
            self.showUI.show()
#         self.showUI.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | self.showUI.windowFlags())
    
    
    def uploadEvent(self):
        """
        上传按钮点击后的触发事件，弹出上传界面窗口
        如果时上传文件到组中时，需要制定访问策略
        """
        #print 'The current index is : ' , self.ui.tabWidget.currentIndex() # 产看当前页面是在个人空间页面还是组空间页面
        
        fd = QtGui.QFileDialog(self)
        fd.setDirectory(QtCore.QString("./datamodel/upload/"))
        if fd.exec_() == QtGui.QDialog.Accepted:
            result = QtCore.QStringList(fd.selectedFiles())
            ans = []
            for i in range(result.count()):
                temp = repr(result[i])
                ans.append(temp)
            del fd
            del result
            
            self.uploadFile['filename'] = repr(ans)
            
            if self.ui.tabWidget.currentIndex() == 0:     # 表示上传到个人空间
                #self.showUI.setFilenames(ans, self.containerName)
                self.uploadFile['username'] = self.userInfo['username']
                self.uploadFile['groupname'] = self.userInfo['username']
                self.uploadFile['container'] = self.containerName
                self.uploadFile['Auth Token'] = self.userInfo['Auth Token']
                self.uploadFile['StorageURL'] = self.userInfo['StorageURL']
                self.showUI.setUploader(self.uploadFile)
                self.uploadFile = {}
                self.showUI.ui.tabWidget.setCurrentWidget(self.showUI.ui.tab)
                self.showInfoWindow()   # show上传下载界面
            else:   # 表示上传到组空间
                if self.currentGroupContainer == None or self.currentGroup == None:
                    QtGui.QMessageBox.about(self, 'Attention', 'Please select the group you want to upload!')
                    return
                if 'GroupAttr' not in self.groupInfo[self.currentGroup]:
                    res = util.groupInfo(self.currentGroup, self.userInfo['username'])
                    ml = []
                    for user in res['users']:
                        ml.append(user['name'])                
                    if self.currentGroup not in self.groupInfo:
                        self.groupInfo[self.currentGroup] = {'GroupAttr':res['account_attr'], 'MemberList' : ','.join(ml), 'GroupInfo': res['account_inst']}
                    else:
                        self.groupInfo[self.currentGroup]['GroupAttr'] = res['account_attr']
                        self.groupInfo[self.currentGroup]['GroupInfo'] = res['account_inst']
                        self.groupInfo[self.currentGroup]['MemberLlist'] = ml
                self.policyDialog.initAttributeList(self.groupInfo[self.currentGroup]['GroupAttr'].split(','))
                self.policyDialog.show()
        else:
            print 'wrong'

    def sureEvent(self, policy):
        print 'The policy is : ', policy
        self.uploadFile['policy'] = str(policy).strip()
        self.uploadFile['username'] = self.userInfo['username']
        self.uploadFile['groupname'] = self.currentGroup
        self.uploadFile['container'] = self.currentGroupContainer
        self.uploadFile['Auth Token'] = self.groupInfo[self.currentGroup]['Auth Token']
        self.uploadFile['StorageURL'] = self.groupInfo[self.currentGroup]['StorageURL']
        print 'sureEvent=======', self.uploadFile
        self.showUI.setUploader(self.uploadFile)
        self.uploadFile = {}
        self.showUI.ui.tabWidget.setCurrentWidget(self.showUI.ui.tab)
        self.showInfoWindow()   # show上传下载界面
        
    def cancelEvent(self, policy):
        self.uploadFile.clear()
        
    
    def downloadEvent(self):
        '''
        下载按钮点击后的触发时间，开始下载
        '''
        print 'start to download'
        for i in range(self.ui.infoTable.rowCount()):
            if self.ui.infoTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                downloadFile = {}
                downloadFile['filename'] = str(self.ui.infoTable.item(i, 1).text())
                downloadFile['group'] = self.userInfo['username']
                downloadFile['container'] = self.containerName
                downloadFile['Auth Token'] = self.userInfo['Auth Token']
                downloadFile['StorageURL'] = self.userInfo['StorageURL']
                self.downloadFiles.append(downloadFile)
        self.showUI.setDownloadFilenames(self.downloadFiles)
        self.downloadFiles = []
        self.showUI.ui.tabWidget.setCurrentWidget(self.showUI.ui.tab_2)
        self.showInfoWindow()   # show 下载界面
        
       
    def addContainerEvent(self):
        '''
        添加新的容器
        '''   
        if self.ui.addButton.text() == 'add':
            self.ui.containerNameEdit.show()  # 显示输入containerName TextEdit 
            self.ui.containerNameEdit.setFocus()
            self.ui.addButton.setText('sure')
        else:
            containerName = str(self.ui.containerNameEdit.text().trimmed()).strip()
            print 'wzb', containerName, '-------------'
            if len(containerName) > 0:
                util.addContainer(self.userInfo['Auth Token'], self.userInfo['StorageURL'],  containerName)
                if self.ui.containerList.count() == 0:
                    self.ui.containerList.addItem(containerName)
                self.ui.containerList.item(self.ui.containerList.count() - 1).setIcon(QtGui.QIcon("res/container.png"))
                self.freshEvent()
            
            self.ui.containerNameEdit.clear()
            self.ui.containerNameEdit.hide()
            self.ui.addButton.setText('add')

        
    def deleteEvent(self):
        '''
        删除选中对象
        '''
#         content = ['-A', 'http://127.0.0.1:8080/auth/v1.0', '-U', 'test:tester', '-K', 'testing','delete', 'wzb']
        content = ['--os-auth-token', self.userInfo['Auth Token'], '--os-storage-url', self.userInfo['StorageURL'], 'delete', self.containerName]
        for i in range(self.ui.infoTable.rowCount()):
            if self.ui.infoTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                content.append(str(self.ui.infoTable.item(i, 1).text()).strip())
        
        # 执行删除对象
        swift.opt(content)
        self.count = 0  # 删除完毕，计数为0
        self.showFrame() # 隐藏frame
        
        # 删除完毕后回调更新列表
        self.freshEvent()
    
    
    def chooseAll(self):
        '''
        复选框全选/或全部取消
        '''
        if self.ui.checkBox.checkState() == QtCore.Qt.Checked:  # 选中状态
            print ''
            self.count = self.ui.infoTable.rowCount()
            self.showFrame()
            for i in range(self.count):
                self.ui.infoTable.item(i, 0).setCheckState(QtCore.Qt.Checked)
        else:
            print ''
            self.count = 0
            self.showFrame()
            for i in range(self.ui.infoTable.rowCount()):
                self.ui.infoTable.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
                        
############################################################################################
############################################################################################
## 组空间处理方法

    ########################
    #激活菜单事件
    @pyqtSignature("QPoint")
    def on_groupTree_customContextMenuRequested(self, point):
        item = self.ui.groupTree.itemAt(point)
        #空白区域不显示菜单
        if item == None:
            self.groupCreateMenuShow()
        else:
            if item.parent() == None:
                self.groupRightMenuShow()
            elif item.parent().parent() == None :
                self.groupDirMenuShow()
            else:
                self.groupItemRightMenuShow()

    def groupCreateMenuShow(self):
        rightMenu = QtGui.QMenu(self.ui.groupTree)
        createAction = QtGui.QAction("add", self, triggered=self.addGroupItem)       
        rightMenu.addAction(createAction)
        rightMenu.exec_(QtGui.QCursor.pos())
        
    #创建右键菜单
    
    def groupRightMenuShow(self):
        rightMenu = QtGui.QMenu(self.ui.groupTree)
        groupInfoAction = QtGui.QAction("group info", self, triggered=self.groupInfoItem)
        rightMenu.addAction(groupInfoAction)
        
        showAction = QtGui.QAction("show containers", self, triggered=self.showContainerItem)       
        rightMenu.addAction(showAction)
        
        memberAction = QtGui.QAction("member list", self, triggered=self.memberGroupItem)
        rightMenu.addAction(memberAction)
        
        showUsrAttrAction = QtGui.QAction("my attributes", self, triggered=self.userAttributeItem)
        rightMenu.addAction(showUsrAttrAction)
        
        createAction = QtGui.QAction("add", self, triggered=self.addGroupItem)       
        rightMenu.addAction(createAction)
        
#         removeAction = QtGui.QAction("delete", self, triggered=self.deleteGroupItem)       
#         rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
    
    def groupInfoItem(self):
        '''
        显示group的详细信息
        '''
        groupName = str(self.ui.groupTree.currentItem().text(0)).strip()
        if groupName not in self.groupInfo or 'GroupAttr' not in self.groupInfo[groupName]: # 表示组的信息还没有缓存时
            print 'add'
            res = util.groupInfo(groupName, self.userInfo['username'])
            ml = []
            for user in res['users']:
                ml.append(user['name'])                
            if groupName not in self.groupInfo:
                self.groupInfo[groupName] = {'GroupAttr':res['account_attr'], 'MemberList' : ml, 'GroupInfo': res['account_inst']}
            else:
                self.groupInfo[groupName]['GroupAttr'] = res['account_attr']
                self.groupInfo[groupName]['GroupInfo'] = res['account_inst']
                self.groupInfo[groupName]['MemberLlist'] = ml
        
        QtGui.QMessageBox.information(self, 'information',  self.groupInfo[groupName]['GroupInfo'] + "\n" + self.groupInfo[groupName]['GroupAttr'] ,  QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
#         QtGui.QMessageBox.about(self, 'infomation', self.groupInfo[groupName]['GroupAttr'] )
#         QtGui.QMessageBox.about(self, 'infomation', self.groupInfo[groupName]['GroupInfo'] )
        #.information(self, 'Attribute',  unquote(ts),  QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
    
    def showContainerItem(self):
        '''
        显示该组内所有的容器, 首先是展开其子列表，然后展开resource的列表，显示所有的容器
        '''
        item = self.ui.groupTree.currentItem()
        self.ui.groupTree.expandItem(item)
        self.ui.groupTree.setCurrentItem(item.child(1))
        self.showCtnItem()
        print '481line:' ,  item.child(1).text(0)
        
    def memberGroupItem(self):
        '''
        显示成员列表
        '''
        groupName = str(self.ui.groupTree.currentItem().text(0)).strip()
        if groupName not in self.groupInfo or 'MemberList' not in self.groupInfo[groupName]: # 表示组的信息还没有缓存时
            res = util.groupInfo(groupName, self.userInfo['username'])
            ml = []
            for user in res['users']:
                ml.append(user['name'])
            if groupName not in self.groupInfo:
                self.groupInfo[groupName] = {'GroupAttr':res['account_attr'], 'MemberList' : ml, 'GroupInfo': res['account_inst']}
            else:
                self.groupInfo[groupName]['GroupAttr'] = res['account_attr']
                self.groupInfo[groupName]['GroupInfo'] = res['account_inst']
                self.groupInfo[groupName]['MemberList'] = ml
                
        self.groupMemberExpanded(self.ui.groupTree.currentItem())
#         QtGui.QMessageBox.about(self, 'member',  ','.join(self.groupInfo[groupName]['MemberList']))
        
        
    def userAttributeItem(self):
        groupName = str(self.ui.groupTree.currentItem().text(0))
        self.currentGroup = groupName
        if groupName not in self.groupInfo or 'StorageURL' not in self.groupInfo[groupName]: # 首次时，向系统获取该组内所有的容器，并更新groupInfo, 及 groupContainers
            command = ['-A', 'http://127.0.0.1:8080/auth/v1.0']
            command.extend(['-U', groupName + ':' + self.userInfo['username'], '-K', self.userInfo['username'], 'stat', '-v'])
            print "command============", command
            result = swift.opt(command)
            if groupName not in self.groupInfo:
                self.groupInfo[groupName] = { 'StorageURL' : result['StorageURL'], 'Auth Token' : result['Auth Token']}
            else:
                self.groupInfo[groupName]['StorageURL'] = result['StorageURL']
                self.groupInfo[groupName]['Auth Token'] = result['Auth Token']
            ctns = []
            for c in util.listContainer(result['Auth Token'], result['StorageURL']):
                ctns.append(c['name'])
            self.groupContainers[groupName] = ctns
        
        attrs = self.groupInfo[groupName]['Auth Token']
        ts = attrs.split('attr')[1]
        QtGui.QMessageBox.information(self, 'Attribute',  unquote(ts),  QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
    def addGroupItem(self):
        '''
        创建群
        '''
        print 'create a group'
    
    def deleteGroupItem(self):
        '''
        删除组
        '''
        print 'delete the group item'
        
    #################
    
    # member list 及 resource的右键菜单
    def groupDirMenuShow(self):
        '''
        二级目录的右键菜单
        '''
        rightMenu = QtGui.QMenu(self.ui.groupTree)
        showContainerAction = QtGui.QAction("show", self, triggered=self.showCtnItem)
        rightMenu.addAction(showContainerAction)
        
        addContainerAction = QtGui.QAction("add", self, triggered=self.addContainerItem)
        rightMenu.addAction(addContainerAction)
        
        rightMenu.exec_(QtGui.QCursor.pos())
    
    # 显示该组的container, 并展开
    def showCtnItem(self):
        print 'show container'
    
        if str(self.ui.groupTree.currentItem().text(0)).strip() != 'members':    # 显示所有的容器
            self.groupContainerExpanded(self.ui.groupTree.currentItem())
            self.ui.groupTree.expandItem(self.ui.groupTree.currentItem())
        else :  # 显示所有的成员
            self.ui.groupTree.setCurrentItem(self.ui.groupTree.currentItem().parent())
            self.memberGroupItem()
            
     
    #######################  
    
    #创建容器右键菜单
    def groupItemRightMenuShow(self):
        rightMenu = QtGui.QMenu(self.ui.groupTree)
        showObjAction = QtGui.QAction("show", self, triggered=self.showObjItem)
        rightMenu.addAction(showObjAction)
    
        addContainerAction = QtGui.QAction("add", self, triggered=self.addContainerItem)
        rightMenu.addAction(addContainerAction)
        
#         deleteContainerAction = QtGui.QAction("delete", self, triggered=self.deleteContainerItem)
#         rightMenu.addAction(deleteContainerAction)
        rightMenu.exec_(QtGui.QCursor.pos())
        
    def showObjItem(self):
        '''
        显示容器内所有的对象
        '''
        item = self.ui.groupTree.currentItem()
        if str(item.parent().text(0)).strip() == 'members':
            return
        self.groupTreeItemClicked(item, 0)
        print item.text(0)    # 获得容器名
        
    def addContainerItem(self):
        '''
        新增一个容器
        '''
        self.ui.lineEdit.show()
        self.ui.lineEdit.clear()
        self.ui.searchButton.setText('sure')
        self.ui.lineEdit.setFocus() # 聚集焦点
        
    def deleteContainerItem(self):
        '''
        删除该容器
        '''
        item  = self.ui.groupTree.currentItem()
        containerName = item.text(0)
        print 'The container name is :', containerName
        util.deleteContainer(self.groupInfo[self.currentGroup]['Auth Token'], self.groupInfo[self.currentGroup]['StorageURL'], containerName)
        self.ui.groupTree.removeItemWidget(item, 0)        
    ######################
    ######################

    def initGroup(self):
        '''
        初始化组空间的控件
        '''
        # 初始化 groupTable
        # 表项不可修改
        self.ui.groupTable.setEditTriggers(QTableWidget.NoEditTriggers)
        # 最后一列拉伸
        self.ui.groupTable.horizontalHeader().setStretchLastSection(True)
        # 设置整行选择
        self.ui.groupTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # 设置第一列的宽度
        self.ui.groupTable.setColumnWidth(0, 23)
        self.ui.groupTable.setColumnWidth(1, 200)
        self.ui.groupTable.setColumnWidth(2, 80)
        self.ui.groupTable.setColumnWidth(3, 120)
        # 设置隔行颜色不同
        self.ui.groupTable.setAlternatingRowColors(True)
        # 不显示网格线
        self.ui.groupTable.setShowGrid(False)
        
        # 添加水平表头
        self.ui.groupTable.setHorizontalHeaderLabels([u' ','filename','size','lastModified', 'uploader'])
        # 设置表头格式
        for n in range(self.ui.groupTable.columnCount()):
            headItem = self.ui.groupTable.horizontalHeaderItem(n)
            headItem.setTextAlignment(0x0001 | 0x0080)  # 设置表头内容居中靠左 QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter
            headItem.setFont(QtGui.QFont("Helvetica"))
            headItem.setBackgroundColor(QtGui.QColor(0,68,10))
            headItem.setTextColor(QtGui.QColor(200,111,30))      
            
    
    def initTree(self):
        '''
        获得所有的组名，并显示在grouptree上
        '''        
        grouplist = self.userInfo['groupList'].split(',')
        for g in grouplist :
            group1 =   QtGui.QTreeWidgetItem(self.ui.groupTree, QtCore.QStringList(QtCore.QString(g.strip())))
            group1.setIcon(0, QtGui.QIcon("res/group.png"))
            group1_1 = QtGui.QTreeWidgetItem(group1, QtCore.QStringList(QtCore.QString('members')))
            group1_1.setIcon(0, QtGui.QIcon("res/member.png"))
            group1.addChild(group1_1)   
            group1_2 = QtGui.QTreeWidgetItem(group1, QtCore.QStringList(QtCore.QString('resources')))
            group1_2.setIcon(0, QtGui.QIcon("res/resource.png"))
            group1.addChild(group1_2)      
     
     
    def searchEvent(self):
        '''
        searchButton触发事件， 当btn名为go时，进行查找；当btn名为sure时，进行增加容器操作
        '''
        btnName = str(self.ui.searchButton.text())
        if btnName == 'search':
            self.ui.searchButton.setText('go')
            self.ui.lineEdit.show()
            self.ui.lineEdit.setFocus()
        elif btnName == 'go':
            # 查找群
            groupName = str(self.ui.lineEdit.text()).strip()
            if len(groupName) == 0:
                self.ui.lineEdit.clear()
                self.ui.lineEdit.hide()
                self.ui.searchButton.setText('search') 
            else:
                # 执行查找
                print 'search group'
        else:
            # 增加容器
            containerName = str(self.ui.lineEdit.text()).strip()
            if len(containerName) == 0:
                self.ui.lineEdit.clear()
                self.ui.lineEdit.hide()
                self.ui.searchButton.setText('search')
            else:
                print 'add container!'
                util.addContainer(self.groupInfo[self.currentGroup]['Auth Token'], self.groupInfo[self.currentGroup]['StorageURL'], containerName)
                self.groupContainers[self.currentGroup].append(containerName)
                if self.ui.groupTree.currentItem().parent().parent() == None:
                    item = self.ui.groupTree.currentItem()
                else:
                    item = self.ui.groupTree.currentItem().parent()
                group1_1 = QtGui.QTreeWidgetItem(item, QtCore.QStringList(QtCore.QString(containerName)))
                group1_1.setIcon(0, QtGui.QIcon("res/container.png"))
                item.addChild(group1_1)
                self.ui.lineEdit.clear()
                self.ui.lineEdit.hide()
                self.ui.searchButton.setText('search')
    
    
    def updateGroupTable(self, result):
        '''
        更新显示组内对象列表
        '''
        count = len(result)
        self.ui.groupTable.setRowCount(count)
        for i in range(0, count):
            item = QtGui.QTableWidgetItem()
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui.groupTable.setItem(i, 0, item)   # 添加复选框
            
            item = QtGui.QTableWidgetItem(result[i]['name'])
            self.ui.groupTable.setItem(i, 1, item)
            
            item = QtGui.QTableWidgetItem()
            size = result[i]['byte_str']
            if 'G' not in size and 'M' not in size or 'K' not in size  or 'B' not in size:
                size = size + 'b'
            item.setText(size)
            self.ui.groupTable.setItem(i, 2, item)
            
            item = QtGui.QTableWidgetItem(result[i]['date'])
            self.ui.groupTable.setItem(i, 3, item)

    
    def groupMemberExpanded(self, item):
        '''
        将组的所有成员显示出来, item 为grouptree的顶层，即组名
        '''
        if item.child(0).child(0) != None:  # 表示组员已经显示出来的情况
            self.ui.groupTree.setCurrentItem(item.child(0))
            return
        ml = self.groupInfo[str(self.ui.groupTree.currentItem().text(0)).strip()]['MemberList']
        print 'the ml is : ' , ml
        for name in ml:
            group1_1 = QtGui.QTreeWidgetItem(item.child(0), QtCore.QStringList(QtCore.QString(name)))
            group1_1.setIcon(0, QtGui.QIcon("res/user.png"))
            item.child(0).addChild(group1_1)
            
        self.ui.groupTree.expandItem(item.child(0))
        self.ui.groupTree.setCurrentItem(item.child(0))
        
    
    def groupContainerExpanded(self, item):
        '''
        展开组下resource的所有子列，即将该组所有的容器显示出来
        '''
        if item.parent() == None:
            return
        
        groupName = str(item.parent().text(0))
        self.currentGroup = groupName
        if groupName not in self.groupInfo or 'StorageURL' not in self.groupInfo[groupName]: # 首次时，向系统获取该组内所有的容器，并更新groupInfo, 及 groupContainers
            command = ['-A', 'http://127.0.0.1:8080/auth/v1.0']
            command.extend(['-U', groupName + ':' + self.userInfo['username'], '-K', self.userInfo['username'], 'stat', '-v'])
            print "command============", command
            result = swift.opt(command)
            if groupName not in self.groupInfo:
                self.groupInfo[groupName] = { 'StorageURL' : result['StorageURL'], 'Auth Token' : result['Auth Token']}
            else:
                self.groupInfo[groupName]['StorageURL'] = result['StorageURL']
                self.groupInfo[groupName]['Auth Token'] = result['Auth Token']
            ctns = []
            for c in util.listContainer(result['Auth Token'], result['StorageURL']):
                ctns.append(c['name'])
            self.groupContainers[groupName] = ctns
#             print '------------', repr(self.groupContainers)    # 打印当前组所有的容器对象
        
        if item.child(0) == None:
            for g in self.groupContainers[groupName]:
                group1_1 = QtGui.QTreeWidgetItem(item, QtCore.QStringList(QtCore.QString(g)))
                group1_1.setIcon(0, QtGui.QIcon("res/container.png"))
                item.addChild(group1_1)
                
            if len(self.groupContainers[groupName]) > 0:    # 若容器存在，则将第一个容器的所有object显示在groupTable中 
                self.groupTreeItemClicked(item.child(0), 0)
        
        
    def groupTreeItemClicked(self, item, column):
        '''
        groupTree中resource下的容器container点击，查看该容器下所有的对象
        容器名为三级目录，故currentGroup = item.parent().parent().text()
        '''
        if item.parent() == None or str(item.parent().text(0)).strip() in self.userInfo['groupList'].split(','):   # 顶层及二级树双击无效
            print 'not container item clcked'
            return
        
        if str(item.parent().text(0)).strip() == 'members': # 点击members中成员时
            print 'click user give nothing'
            return
        
        # 底层容器被双击，即查看对应容器的内容 
        self.currentGroup = str(item.parent().parent().text(0)).strip()
        self.currentGroupContainer = str(item.text(column)).strip()    # 获得容器名
        # 获得该组 ctn容器下所有的对象，并显示出来
        result = util.listObject(self.groupInfo[self.currentGroup]['Auth Token'], self.groupInfo[self.currentGroup]['StorageURL'], self.currentGroupContainer)
        if result != None:
            self.updateGroupTable(result)
    
    
    def groupTableItemClicked(self, item):
        '''
        groupTable中item选中或取消
        '''
        row = item.row()
        column = item.column()
        if column != 0:
            if self.ui.groupTable.item(row,0).checkState() == QtCore.Qt.Checked:            
                self.ui.groupTable.item(row,0).setCheckState(QtCore.Qt.Unchecked)
                self.count2 = self.count2 - 1
            else:            
                self.ui.groupTable.item(row, 0).setCheckState(QtCore.Qt.Checked)
                self.count2 = self.count2 + 1
        else:
            if self.ui.groupTable.item(row,0).checkState() == QtCore.Qt.Checked:       
                self.count2 = self.count2 + 1
            else:                  
                self.count2 = self.count2- 1
    
    def downloadEvent2(self):
        '''
        群内容下载
        '''
        for i in range(self.ui.groupTable.rowCount()):
            if self.ui.groupTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                downloadFile = {}
                downloadFile['filename'] = str(self.ui.groupTable.item(i, 1).text())
                downloadFile['group'] = self.currentGroup
                downloadFile['container'] = self.currentGroupContainer
                downloadFile['Auth Token'] = self.groupInfo[self.currentGroup]['Auth Token']
                downloadFile['StorageURL'] = self.groupInfo[self.currentGroup]['StorageURL']
                self.downloadFiles.append(downloadFile)
        self.showUI.setDownloadFilenames(self.downloadFiles)
        self.downloadFiles = []
        self.showUI.ui.tabWidget.setCurrentWidget(self.showUI.ui.tab_2)
        self.showInfoWindow()   # show 下载界面
        
    def chooseAll2(self):
        '''
        复选框全选/或全部取消
        '''
        if self.ui.checkBox2.checkState() == QtCore.Qt.Checked:  # 选中状态
            self.count2 = self.ui.groupTable.rowCount()
            for i in range(self.count2):
                self.ui.groupTable.item(i, 0).setCheckState(QtCore.Qt.Checked)
        else:
            self.count2 = 0
            for i in range(self.ui.groupTable.rowCount()):
                self.ui.groupTable.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
    
    def deleteEvent2(self):
        '''
        删除组内对象
        '''
        content = ['--os-auth-token', self.groupInfo[self.currentGroup]['Auth Token'], '--os-storage-url', self.groupInfo[self.currentGroup]['StorageURL'], 'delete', self.currentGroupContainer]
        for i in range(self.ui.groupTable.rowCount()):
            if self.ui.groupTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                content.append(str(self.ui.groupTable.item(i, 1).text()).strip())
        
        # 执行删除对象
        swift.opt(content)
        self.count2 = 0  # 删除完毕，计数为0
        
        # 删除完毕后回调更新列表
        self.freshGroupTable()
        
    def freshGroupTable(self):
        result = util.listObject(self.groupInfo[self.currentGroup]['Auth Token'], self.groupInfo[self.currentGroup]['StorageURL'], self.currentGroupContainer)
        self.updateGroupTable(result)