# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1688, 1110)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidgetComputers = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidgetComputers.setGeometry(QtCore.QRect(10, 20, 401, 971))
        self.treeWidgetComputers.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.treeWidgetComputers.setTabKeyNavigation(True)
        self.treeWidgetComputers.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.treeWidgetComputers.setObjectName("treeWidgetComputers")
        self.treeWidgetComputers.headerItem().setText(0, "1")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(420, 20, 1251, 1031))
        self.tabWidget.setObjectName("tabWidget")
        self.system_tab = QtWidgets.QWidget()
        self.system_tab.setObjectName("system_tab")
        self.SendRunProcessBtn = QtWidgets.QPushButton(self.system_tab)
        self.SendRunProcessBtn.setGeometry(QtCore.QRect(170, 950, 151, 41))
        self.SendRunProcessBtn.setToolTipDuration(5)
        self.SendRunProcessBtn.setObjectName("SendRunProcessBtn")
        self.treeWidgetProcess = QtWidgets.QTreeWidget(self.system_tab)
        self.treeWidgetProcess.setGeometry(QtCore.QRect(10, 30, 1081, 911))
        self.treeWidgetProcess.setObjectName("treeWidgetProcess")
        self.treeWidgetProcess.headerItem().setText(0, "1")
        self.SendMessageBtn = QtWidgets.QPushButton(self.system_tab)
        self.SendMessageBtn.setGeometry(QtCore.QRect(670, 950, 111, 41))
        self.SendMessageBtn.setToolTipDuration(5)
        self.SendMessageBtn.setObjectName("SendMessageBtn")
        self.textEdit = QtWidgets.QTextEdit(self.system_tab)
        self.textEdit.setGeometry(QtCore.QRect(790, 950, 271, 41))
        self.textEdit.setObjectName("textEdit")
        self.RunProcessTextEdit = QtWidgets.QTextEdit(self.system_tab)
        self.RunProcessTextEdit.setGeometry(QtCore.QRect(330, 950, 201, 41))
        self.RunProcessTextEdit.setObjectName("RunProcessTextEdit")
        self.SendKillProcessBtn = QtWidgets.QPushButton(self.system_tab)
        self.SendKillProcessBtn.setGeometry(QtCore.QRect(10, 950, 151, 41))
        self.SendKillProcessBtn.setToolTipDuration(5)
        self.SendKillProcessBtn.setObjectName("SendKillProcessBtn")
        self.MessageRecv_3 = QtWidgets.QLabel(self.system_tab)
        self.MessageRecv_3.setGeometry(QtCore.QRect(10, 0, 121, 31))
        self.MessageRecv_3.setObjectName("MessageRecv_3")
        self.SelectedMachineLbl = QtWidgets.QLabel(self.system_tab)
        self.SelectedMachineLbl.setGeometry(QtCore.QRect(130, 0, 91, 31))
        self.SelectedMachineLbl.setObjectName("SelectedMachineLbl")
        self.tabWidget.addTab(self.system_tab, "")
        self.functionnal_tab = QtWidgets.QWidget()
        self.functionnal_tab.setObjectName("functionnal_tab")
        self.tabWidget.addTab(self.functionnal_tab, "")
        self.MessageRecv_2 = QtWidgets.QLabel(self.centralwidget)
        self.MessageRecv_2.setGeometry(QtCore.QRect(290, 1050, 91, 31))
        self.MessageRecv_2.setObjectName("MessageRecv_2")
        self.MessageRecv = QtWidgets.QLabel(self.centralwidget)
        self.MessageRecv.setGeometry(QtCore.QRect(390, 1050, 621, 31))
        self.MessageRecv.setWordWrap(True)
        self.MessageRecv.setObjectName("MessageRecv")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TestRunner"))
        MainWindow.setToolTip(_translate("MainWindow", "Sends a texte message to selected computers"))
        self.SendRunProcessBtn.setToolTip(_translate("MainWindow", "Sends a texte message to selected computers"))
        self.SendRunProcessBtn.setText(_translate("MainWindow", "Run Programme"))
        self.SendMessageBtn.setToolTip(_translate("MainWindow", "Sends a texte message to selected computers"))
        self.SendMessageBtn.setText(_translate("MainWindow", "Send Message to \n"
"selected machine"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.RunProcessTextEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.SendKillProcessBtn.setToolTip(_translate("MainWindow", "Sends a texte message to selected computers"))
        self.SendKillProcessBtn.setText(_translate("MainWindow", "Kill Selected Process"))
        self.MessageRecv_3.setText(_translate("MainWindow", "Running processes of :"))
        self.SelectedMachineLbl.setText(_translate("MainWindow", "Machine X"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.system_tab), _translate("MainWindow", "System"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.functionnal_tab), _translate("MainWindow", "Autotest"))
        self.MessageRecv_2.setText(_translate("MainWindow", "Received Message"))
        self.MessageRecv.setText(_translate("MainWindow", "..."))
