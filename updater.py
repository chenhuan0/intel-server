#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
from PyQt4 import QtCore, QtGui
import time
import shutil
import os
import contentdeliver

class CUpdater(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def setNames(self, root, serial):
        self.serial = serial
        self.root = root
        self.dbPath = root + USER_DB_PATH
        self.videoPath = root + USER_VIDEOS_PATH;
        self.previewsPath = root + USER_PREVIEWS_PATH;

    def run(self):
        msg = QtGui.QApplication.translate('updater', "Updating index database of device(%1).").arg(self.serial)
        self.emit(QtCore.SIGNAL("sendmsg"), msg, "blue")
        self.updateIndex()
        time.sleep(3)
        msg = QtGui.QApplication.translate('updater', "Updating resource files of device(%1).").arg(self.serial)
        self.emit(QtCore.SIGNAL("sendmsg"), msg, "blue")
        self.updateContent()
        time.sleep(3)
        msg = QtGui.QApplication.translate('updater', "Syncing device(%1) with system.").arg(self.serial)
        self.emit(QtCore.SIGNAL("sendmsg"), msg, "blue")
        os.system('sync')
        msg = QtGui.QApplication.translate('updater', "Device(%1) is updated.").arg(self.serial)
        self.emit(QtCore.SIGNAL("sendmsg"), msg, "blue")

    def updateIndex(self):
        #Update index database
        if os.path.exists(self.dbPath):
            shutil.rmtree(self.dbPath)
        shutil.copytree(SERVER_DB_PATH, self.dbPath)
        #Update preview images
        if os.path.exists(self.previewsPath):
            shutil.rmtree(self.previewsPath)

        shutil.copytree(SERVER_PREVIEWS_PATH, self.previewsPath)

    def updateContent(self):
        deliver = contentdeliver.contentDeliver(self.root) 
        try:
            deliver.run()
        except Exception, e:
            msg = QtGui.QApplication.translate('updater', "Error of device(%1): %2").arg(self.serial).arg(str(e))
            self.emit(QtCore.SIGNAL("sendmsg"), msg, "blue")
