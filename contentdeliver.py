#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os 
from config import *
import shutil
from PyQt4 import QtCore, QtGui

class contentDeliver(QtCore.QObject):
    sendmsg = QtCore.pyqtSignal(str, str)
    def __init__(self, root, serial):
        QtCore.QObject.__init__(self)
        self.videopath = root + USER_VIDEOS_PATH
        self.interest = root + USER_INTEREST_FILE
        self.todel = root + USER_DEL_FILE
        self.indevice = root + USER_HAVE_FILE

        self.sqliteConn = sqlite3.connect(SERVER_DB_FILE)
        self.sqliteCur = self.sqliteConn.cursor() 
        self.serial = serial

    def run(self):
        interestFile = open(self.interest, "r")
        delFile = open(self.todel, "r")

        if not os.path.exists(self.videopath):
            os.mkdir(self.videopath)
        if os.path.isfile(self.indevice):
            os.remove(self.indevice)
        for line in interestFile:
            contentID = int(line)
            sql = "select * from contents where id = " + str(contentID)
            self.sqliteCur.execute(sql)
            result = self.sqliteCur.fetchall()
            title = result[0][1]
            filename = result[0][2]
            mainclass = result[0][4]
            subclass = result[0][5]
            self.sendContent(filename, title)
            self.updateIndevice(contentID, mainclass, subclass)

        interestFile.close()

        for line in delFile:
            contentID = int(line)
            sql = "select * from contents where id = " + str(contentID)
            self.sqliteCur.execute(sql)
            result = self.sqliteCur.fetchall()
            filename = result[0][2]
            title = result[0][1]
            self.delContent(filename, title)

        delFile.close()

    def sendContent(self, filename, title):
        filepath = SERVER_VIDEOS_PATH + filename
        if not os.path.isfile(self.videopath + filename):
            shutil.copy(filepath, self.videopath + filename)
            msg = QtGui.QApplication.translate('contentdeliver', "Copy %1 to device(%2)...").arg(title).arg(self.serial)
            self.sendmsg.emit(msg, "blue")

    def delContent(self, filename, title):
        if os.path.isfile(self.videopath + filename):
            os.remove(self.videopath + filename)
            msg = QtGui.QApplication.translate('contentdeliver', "Delete %1 from device(%2)...").arg(title).arg(self.serial)
            self.sendmsg.emit(msg, "blue")

    def updateIndevice(self, contentID, mainclass, subclass):
        indevice = open(self.indevice, "a")
        line = str(mainclass) + "###" + str(subclass) + "###" + str(contentID) + os.linesep
        indevice.writelines(line)
        indevice.close()