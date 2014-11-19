#/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wuzebang 2014/1/7

## username: test:tester    password: testing
## username: test2:tester2  password: testing2
from PyQt4 import QtGui, QtCore
import sys

from mainUI import MyForm
from o_loginUI import Ui_loginForm
import swift_test as swift


class MyLogin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # 窗体居中显示，且大小不可变
        self.setFixedSize(447,290)
        width = QtGui.QApplication.desktop().width() - 447
        height = QtGui.QApplication.desktop().height() - 290
        self.move(width / 2, height / 2)
        
        self.ui = Ui_loginForm()
        self.ui.setupUi(self)
        self.setWindowTitle('login dialog')
#         self.mainWindow = MyForm()
#         self.mainWindow.hide()
        
        
        QtCore.QObject.connect(self.ui.loginButton, QtCore.SIGNAL('clicked()'), self.login)
        
    
    def login(self):
        username = str(self.ui.usernameEdit.text().trimmed())
        password = str(self.ui.passwordEdit.text().trimmed())
        if username == '' :
            self.ui.infoLabel.setText("input username")
            self.ui.usernameEdit.setFocus()
            return 
        if password =='':
            self.ui.infoLabel.setText("Input password")
            self.ui.passwordEdit.setFocus()
            return
        
        print 'username is : ', username
        print 'password is : ', password
        
        command = ['-A', 'http://127.0.0.1:8080/auth/v1.0']
        command.extend(['-U', username+':' + username , '-K', password, 'stat', '-v'])
        result = swift.opt(command)
        
        print 'The result is : ' , result
        
        if result is not None:
            info = {'Auth Token': result['Auth Token'], 
                        'StorageURL':result['StorageURL'], 
                        'groupList': result['x-user-group'],
                        'username' : username
                        }
            self.mainWindow = MyForm()
            self.mainWindow.show()
            self. mainWindow.setUserInfo(info)
            self.mainWindow.freshEvent()
            self.close()
        else:
            self.ui.infoLabel.setText("username or password error")
            self.ui.passwordEdit.clear()
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyLogin()
    myapp.show()
    
    sys.exit(app.exec_())