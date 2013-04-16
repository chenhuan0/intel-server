#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
from PyQt4 import QtCore, QtGui
import time
import shutil
import os
import contentdeliver
import dbus

class CUpdater(QtCore.QThread):
    sendmsg = QtCore.pyqtSignal(str, str)
    finished = QtCore.pyqtSignal(dbus.String, dbus.proxies.ProxyObject)
    def __init__(self, parent, deviceObj):
        QtCore.QThread.__init__(self)
        self.parent = parent
        self.deviceObj = deviceObj

    def setNames(self, root, serial):
        self.serial = serial
        self.root = root
        self.dbPath = root + USER_DB_PATH
        self.videoPath = root + USER_VIDEOS_PATH;
        self.previewsPath = root + USER_PREVIEWS_PATH;

    def run(self):
        msg = QtGui.QApplication.translate('updater', "Updating index database of device(%1)...").arg(self.serial)
        self.sendmsg.emit(msg, "blue")
        self.updateIndex()
        time.sleep(3)
        msg = QtGui.QApplication.translate('updater', "Updating resource files of device(%1)....").arg(self.serial)
        self.sendmsg.emit(msg, "blue")
        self.updateContent()
        time.sleep(3)
        msg = QtGui.QApplication.translate('updater', "Syncing device(%1) with system...").arg(self.serial)
        self.sendmsg.emit(msg, "blue")
        os.system('sync')
        msg = QtGui.QApplication.translate('updater', "Device(%1) is updated").arg(self.serial)
        self.sendmsg.emit(msg, "blue")

        self.finished.emit(self.serial, self.deviceObj)
        

    def updateIndex(self):
        try:
            #Update index database
            if os.path.exists(self.dbPath):
                shutil.rmtree(self.dbPath)
            shutil.copytree(SERVER_DB_PATH, self.dbPath)
            #Update preview images
            if os.path.exists(self.previewsPath):
                shutil.rmtree(self.previewsPath)

            shutil.copytree(SERVER_PREVIEWS_PATH, self.previewsPath)
        except Exception, e:
            msg = QtGui.QApplication.translate('updater', "Error of device(%1): %2").arg(self.serial).arg(str(e))
            self.sendmsg.emit(msg, "blue")

    def updateContent(self):      
        try:
            deliver = contentdeliver.contentDeliver(self.root, self.serial) 
            deliver.sendmsg[str, str].connect(self.parent.message, QtCore.Qt.QueuedConnection)
            deliver.run()
        except Exception, e:
            msg = QtGui.QApplication.translate('updater', "Error of device(%1): %2").arg(self.serial).arg(str(e))
            self.sendmsg.emit(msg, "blue")
