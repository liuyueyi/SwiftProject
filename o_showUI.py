# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showUI.ui'
#
# Created: Wed Feb 26 09:51:36 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_showWindow(object):
    def setupUi(self, showWindow):
        showWindow.setObjectName(_fromUtf8("showWindow"))
        showWindow.resize(506, 749)
        self.tabWidget = QtGui.QTabWidget(showWindow)
        self.tabWidget.setGeometry(QtCore.QRect(0, 10, 501, 731))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uploadTable = QtGui.QTableWidget(self.tab)
        self.uploadTable.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.uploadTable.setRowCount(0)
        self.uploadTable.setColumnCount(6)
        self.uploadTable.setObjectName(_fromUtf8("uploadTable"))
        self.uploadTable.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.uploadTable)
        self.frame = QtGui.QFrame(self.tab)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout.addWidget(self.checkBox)
        self.encryptCheckBox = QtGui.QCheckBox(self.frame)
        self.encryptCheckBox.setObjectName(_fromUtf8("encryptCheckBox"))
        self.horizontalLayout.addWidget(self.encryptCheckBox)
        self.auditCheckBox = QtGui.QCheckBox(self.frame)
        self.auditCheckBox.setObjectName(_fromUtf8("auditCheckBox"))
        self.horizontalLayout.addWidget(self.auditCheckBox)
        self.startButton = QtGui.QPushButton(self.frame)
        self.startButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.horizontalLayout.addWidget(self.startButton)
        self.deleteButton = QtGui.QPushButton(self.frame)
        self.deleteButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout.addWidget(self.frame)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.downloadTable = QtGui.QTableWidget(self.tab_2)
        self.downloadTable.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.downloadTable.setColumnCount(5)
        self.downloadTable.setObjectName(_fromUtf8("downloadTable"))
        self.downloadTable.setRowCount(0)
        self.downloadTable.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.downloadTable)
        self.frame2 = QtGui.QFrame(self.tab_2)
        self.frame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame2.setObjectName(_fromUtf8("frame2"))
        self.gridLayout = QtGui.QGridLayout(self.frame2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.deleteButton2 = QtGui.QPushButton(self.frame2)
        self.deleteButton2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.deleteButton2.setObjectName(_fromUtf8("deleteButton2"))
        self.gridLayout.addWidget(self.deleteButton2, 0, 3, 1, 1)
        self.checkBox2 = QtGui.QCheckBox(self.frame2)
        self.checkBox2.setObjectName(_fromUtf8("checkBox2"))
        self.gridLayout.addWidget(self.checkBox2, 0, 0, 1, 1)
        self.startButton2 = QtGui.QPushButton(self.frame2)
        self.startButton2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.startButton2.setObjectName(_fromUtf8("startButton2"))
        self.gridLayout.addWidget(self.startButton2, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.frame2)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))

        self.retranslateUi(showWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(showWindow)

    def retranslateUi(self, showWindow):
        showWindow.setWindowTitle(_translate("showWindow", "upload/download UI", None))
        self.checkBox.setText(_translate("showWindow", "all", None))
        self.encryptCheckBox.setText(_translate("showWindow", "encrypt", None))
        self.auditCheckBox.setText(_translate("showWindow", "audit", None))
        self.startButton.setText(_translate("showWindow", "Start", None))
        self.deleteButton.setText(_translate("showWindow", "delete", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("showWindow", "upload", None))
        self.deleteButton2.setText(_translate("showWindow", "delete", None))
        self.checkBox2.setText(_translate("showWindow", "all", None))
        self.startButton2.setText(_translate("showWindow", "Start", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("showWindow", "download", None))

