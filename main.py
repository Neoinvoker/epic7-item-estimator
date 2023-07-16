from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication

from adbutils import adb, AdbDevice, errors
from numpy import asarray

import random
import sys
from ADBManager import ADBManager
from GUI import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
