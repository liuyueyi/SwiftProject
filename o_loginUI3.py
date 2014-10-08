# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginUI.ui'
#
# Created: Wed Mar  5 13:46:21 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_loginForm(object):
    def setupUi(self, loginForm):
        loginForm.setObjectName(_fromUtf8("loginForm"))
        loginForm.resize(447, 290)
        self.frame = QtGui.QFrame(loginForm)
        self.frame.setGeometry(QtCore.QRect(10, 40, 431, 211))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.usernameEdit = QtGui.QLineEdit(self.frame)
        self.usernameEdit.setObjectName(_fromUtf8("usernameEdit"))
        self.gridLayout.addWidget(self.usernameEdit, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 1)
        self.passwordEdit = QtGui.QLineEdit(self.frame)
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordEdit.setObjectName(_fromUtf8("passwordEdit"))
        self.gridLayout.addWidget(self.passwordEdit, 1, 2, 1, 1)
        self.loginButton = QtGui.QPushButton(self.frame)
        self.loginButton.setMinimumSize(QtCore.QSize(0, 40))
        self.loginButton.setMaximumSize(QtCore.QSize(80, 100))
        self.loginButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.loginButton.setObjectName(_fromUtf8("loginButton"))
        self.gridLayout.addWidget(self.loginButton, 2, 2, 1, 1)
        self.label = QtGui.QLabel(self.frame)
        self.label.setMinimumSize(QtCore.QSize(100, 60))
        self.label.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setMinimumSize(QtCore.QSize(0, 60))
        self.label_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.infoLabel = QtGui.QLabel(self.frame)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(159, 158, 158))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.infoLabel.setPalette(palette)
        self.infoLabel.setText(_fromUtf8(""))
        self.infoLabel.setObjectName(_fromUtf8("infoLabel"))
        self.gridLayout.addWidget(self.infoLabel, 3, 2, 1, 1)
        self.label_3 = QtGui.QLabel(loginForm)
        self.label_3.setGeometry(QtCore.QRect(0, 10, 74, 18))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.registButton = QtGui.QPushButton(loginForm)
        self.registButton.setGeometry(QtCore.QRect(360, 261, 80, 28))
        self.registButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.registButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.registButton.setObjectName(_fromUtf8("registButton"))
        self.label_4 = QtGui.QLabel(loginForm)
        self.label_4.setGeometry(QtCore.QRect(90, 260, 251, 31))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(loginForm)
        QtCore.QMetaObject.connectSlotsByName(loginForm)
        loginForm.setTabOrder(self.usernameEdit, self.passwordEdit)
        loginForm.setTabOrder(self.passwordEdit, self.loginButton)
        loginForm.setTabOrder(self.loginButton, self.registButton)

    def retranslateUi(self, loginForm):
        loginForm.setWindowTitle(QtGui.QApplication.translate("loginForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.usernameEdit.setText(QtGui.QApplication.translate("loginForm", "wzb", None, QtGui.QApplication.UnicodeUTF8))
        self.passwordEdit.setText(QtGui.QApplication.translate("loginForm", "wzb", None, QtGui.QApplication.UnicodeUTF8))
        self.loginButton.setText(QtGui.QApplication.translate("loginForm", "登陆", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("loginForm", "用户名：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("loginForm", "密码：", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("loginForm", "登陆窗口", None, QtGui.QApplication.UnicodeUTF8))
        self.registButton.setText(QtGui.QApplication.translate("loginForm", "注册", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("loginForm", "还没有帐号，点击右边按钮快速注册", None, QtGui.QApplication.UnicodeUTF8))

