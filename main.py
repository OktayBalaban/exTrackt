# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 13:41:56 2023

@author: oktay
"""

from PyQt5 import QtWidgets
from gui import MainWindow

import warnings
from filelock import FileLock, Timeout

lock = FileLock("my_app.lock")

try:
    with lock.acquire(timeout=30): # Due to a bug of multiple openings of app, lock is present.
        app = QtWidgets.QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()
except Timeout:
    print("Another instance of this application is already running.")