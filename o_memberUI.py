# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'memberUI.ui'
#
# Created: Thu Feb 27 11:30:50 2014
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

class Ui_memberDialog(object):
    def setupUi(self, memberDialog):
        memberDialog.setObjectName(_fromUtf8("memberDialog"))
        memberDialog.resize(498, 587)
        self.memberList = QtGui.QListWidget(memberDialog)
        self.memberList.setGeometry(QtCore.QRect(0, 30, 191, 551))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(50)
        font.setKerning(True)
        self.memberList.setFont(font)
        self.memberList.setObjectName(_fromUtf8("memberList"))
        item = QtGui.QListWidgetItem()
        self.memberList.addItem(item)
        self.label_2 = QtGui.QLabel(memberDialog)
        self.label_2.setGeometry(QtCore.QRect(200, 10, 131, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label = QtGui.QLabel(memberDialog)
        self.label.setGeometry(QtCore.QRect(0, 10, 191, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.attributeTable = QtGui.QTableWidget(memberDialog)
        self.attributeTable.setGeometry(QtCore.QRect(200, 30, 291, 551))
        self.attributeTable.setRowCount(0)
        self.attributeTable.setColumnCount(2)
        self.attributeTable.setObjectName(_fromUtf8("attributeTable"))
        self.attributeTable.verticalHeader().setVisible(False)

        self.retranslateUi(memberDialog)
        QtCore.QMetaObject.connectSlotsByName(memberDialog)

    def retranslateUi(self, memberDialog):
        memberDialog.setWindowTitle(_translate("memberDialog", "Dialog", None))
        __sortingEnabled = self.memberList.isSortingEnabled()
        self.memberList.setSortingEnabled(False)
        item = self.memberList.item(0)
        item.setText(_translate("memberDialog", "吴泽邦", None))
        self.memberList.setSortingEnabled(__sortingEnabled)
        self.label_2.setText(_translate("memberDialog", "attributes:", None))
        self.label.setText(_translate("memberDialog", "group members:", None))

