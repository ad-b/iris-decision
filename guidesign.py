# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1068, 690)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lFile = QtWidgets.QLabel(self.centralwidget)
        self.lFile.setGeometry(QtCore.QRect(30, 30, 640, 480))
        self.lFile.setFrameShape(QtWidgets.QFrame.Box)
        self.lFile.setAlignment(QtCore.Qt.AlignCenter)
        self.lFile.setObjectName("lFile")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(30, 530, 641, 91))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.bCamera = QtWidgets.QPushButton(self.splitter)
        self.bCamera.setObjectName("bCamera")
        self.bCamera_2 = QtWidgets.QPushButton(self.splitter)
        self.bCamera_2.setObjectName("bCamera_2")
        self.bFile = QtWidgets.QPushButton(self.splitter)
        self.bFile.setObjectName("bFile")
        self.splitter_4 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_4.setGeometry(QtCore.QRect(690, 30, 361, 591))
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setObjectName("splitter_4")
        self.bCompare = QtWidgets.QPushButton(self.splitter_4)
        self.bCompare.setObjectName("bCompare")
        self.splitter_2 = QtWidgets.QSplitter(self.splitter_4)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.widget = QtWidgets.QWidget(self.splitter_2)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.edit_ID = QtWidgets.QLineEdit(self.widget)
        self.edit_ID.setObjectName("edit_ID")
        self.verticalLayout.addWidget(self.edit_ID)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.edit_photonr = QtWidgets.QLineEdit(self.widget)
        self.edit_photonr.setObjectName("edit_photonr")
        self.verticalLayout.addWidget(self.edit_photonr)
        self.bAdd = QtWidgets.QPushButton(self.splitter_2)
        self.bAdd.setObjectName("bAdd")
        self.splitter_3 = QtWidgets.QSplitter(self.splitter_4)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.buttonHello = QtWidgets.QPushButton(self.splitter_3)
        self.buttonHello.setObjectName("buttonHello")
        self.bParameters = QtWidgets.QPushButton(self.splitter_3)
        self.bParameters.setObjectName("bParameters")
        self.textOutput = QtWidgets.QTextBrowser(self.splitter_4)
        self.textOutput.setObjectName("textOutput")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1068, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lFile.setText(_translate("MainWindow", "Open camera or image from file"))
        self.bCamera.setText(_translate("MainWindow", "Open camera"))
        self.bCamera_2.setText(_translate("MainWindow", "Save picture"))
        self.bFile.setText(_translate("MainWindow", "Open from file"))
        self.bCompare.setText(_translate("MainWindow", "Compare with database"))
        self.label.setText(_translate("MainWindow", "Person ID"))
        self.label_2.setText(_translate("MainWindow", "Photo number"))
        self.bAdd.setText(_translate("MainWindow", "Add to database"))
        self.buttonHello.setText(_translate("MainWindow", "hello"))
        self.bParameters.setText(_translate("MainWindow", "Parameters"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

