#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2014/2/27
# 用来处理主界面
# from PyQt4 import QtGui, QtCore
# from o_memberUI import Ui_memberDialog
# 
# def __init__(self, parent=None):
#     QtGui.QWidget.__init__(self, parent)
#     self.ui = Ui_memberDialog()
#     self.ui.setupUi(self)


from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignature

class Ui_formDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        uic.loadUi("memberUI.ui", self)
        
        self.setFixedSize(170, 752)
        self.frame.resize(170, 721)
        self.initTable()
        
        item = ['OaK','Banana','Apple','Orange','Grapes','Jayesh']
        self.listDataBind(item)
        self.memberList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)   #定义右键菜单
        self.memberList.setSortingEnabled(True) # 设置自动排序

    
    def initTable(self):
        # 表项不可修改
        self.attributeTable.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        # 最后一列拉伸
        self.attributeTable.horizontalHeader().setStretchLastSection(True)
        #
        self.attributeTable.setColumnWidth(0, 150)
        # 设置整行选择
        self.attributeTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # 设置隔行颜色不同
        self.attributeTable.setAlternatingRowColors(True)
        # 不显示网格线
        self.attributeTable.setShowGrid(False)
        # 添加水平表头
        self.attributeTable.setHorizontalHeaderLabels(['attribute name', 'attribute value'])
        # 设置表头格式
        for n in range(self.attributeTable.columnCount()):
            headItem = self.attributeTable.horizontalHeaderItem(n)
#             headItem.setTextAlignment(0x0001 | 0x0080)  # 设置表头内容居中靠左 QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter
            headItem.setFont(QtGui.QFont("Helvetica"))
            headItem.setBackgroundColor(QtGui.QColor(0,68,10))
            headItem.setTextColor(QtGui.QColor(200,111,30))     
        self.attributeTable.hide()
    
    def listDataBind(self, item):
        for lst in item:
            self.memberList.addItem(QtGui.QListWidgetItem(lst))
            
    #激活菜单事件
    @pyqtSignature("QPoint")
    def on_memberList_customContextMenuRequested(self, point):
        item = self.memberList.itemAt(point)
        #空白区域不显示菜单
        if item != None:
            self.rightMenuShow()

    #创建右键菜单
    def rightMenuShow(self):
        rightMenu = QtGui.QMenu(self.memberList)
        infoAction = QtGui.QAction(u"info", self, triggered=self.showInfoItem)       # triggered 为右键菜单点击后的激活事件
        rightMenu.addAction(infoAction)
        
        hideAction = QtGui.QAction(u"hide", self, triggered=self.hideInfoItem)       # triggered 为右键菜单点击后的激活事件
        rightMenu.addAction(hideAction)
       
        removeAction = QtGui.QAction(u"delete", self, triggered=self.deleteItem)       # 也可以指定自定义对象事件
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QtGui.QCursor.pos())
        
    def hideInfoItem(self):
        self.attributeTable.hide()
        self.setFixedSize(170, 752)
        self.frame.resize(170, 721)
        
    def deleteItem(self):
        row = self.memberList.currentRow()
        self.memberList.takeItem(row)
        print "The selected row is : " , row
    
    def showInfoItem(self):
        '''
        将用户属性详细的显示在右端
        '''
        self.attributeTable.show()
        self.setFixedSize(476, 752)
        self.frame.resize(471, 721)
        
        
# if __name__ == "__main__":
#     app = QtGui.QApplication(sys.argv)
#     myapp = Ui_formDialog()
#     myapp.show()
#     
#     sys.exit(app.exec_())