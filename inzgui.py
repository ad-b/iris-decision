# -*- coding: utf-8 -*-
import sys
import subprocess
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap
from guidesign import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    fname = ''
    path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.buttonHello.clicked.connect(self.write_hello)
        self.bFile.clicked.connect(self.open_file)
        self.bCompare.clicked.connect(self.compare)

    def compare(self):
        cmd_line = ['python', self.path + '\\Decide.py', '-i', self.fname, '-m 8']
        output = subprocess.Popen(cmd_line, universal_newlines=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  bufsize=1)
        while True:
            line = output.stdout.readline()
            if not line:
                break
            self.textOutput.append(line[:-1])

    def open_file(self):
        self.fname, _ = QFileDialog.getOpenFileName(self, 'Open file', 'D:\\PyCharm\\inz\\test\\')
        self.textOutput.append("Opened image " + self.fname)
        pixmap = QPixmap(self.fname)
        self.lFile.setScaledContents(True)
        self.lFile.setPixmap(pixmap)

    def write_hello(self):
        hello_string = "Cześć :)"
        self.textOutput.append(hello_string)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
