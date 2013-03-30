#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os 
from config import *
import shutil

class contentDeliver(object):
    def __init__(self, root):
        self.videopath = root + USER_VIDEOS_PATH
        self.interest = root + USER_INTEREST_FILE
        self.todel = root + USER_DEL_FILE
        self.indevice = root + USER_HAVE_FILE

        self.sqliteConn = sqlite3.connect(SERVER_DB_FILE)
        self.sqliteCur = self.sqliteConn.cursor() 

    def run(self):

        interestFile = open(self.interest, "r")
        delFile = open(self.todel, "r")

        if not os.path.exists(self.videopath):
            os.mkdir(self.videopath)
        os.remove(self.indevice)
        for line in interestFile:
            contentID = int(line)
            sql = "select * from contents where id = " + str(contentID)
            self.sqliteCur.execute(sql)
            result = self.sqliteCur.fetchall()
            filename = result[0][2]
            mainclass = result[0][4]
            subclass = result[0][5]
            self.sendContent(filename)
            self.updateIndevice(contentID, mainclass, subclass)

        interestFile.close()

        for line in delFile:

            contentID = int(line)
            sql = "select * from contents where id = " + str(contentID)
            self.sqliteCur.execute(sql)
            result = self.sqliteCur.fetchall()
            filename = result[0][2]
            
            self.delContent(filename)

        delFile.close()

    def sendContent(self, filename):
        filepath = SERVER_VIDEOS_PATH + filename
        if not os.path.isfile(self.videopath + filename):
            shutil.copy(filepath, self.videopath + filename)

    def delContent(self, filename):
        if os.path.isfile(self.videopath + filename):
            os.remove(self.videopath + filename)

    def updateIndevice(self, contentID, mainclass, subclass):
        indevice = open(self.indevice, "a")
        line = str(mainclass) + "###" + str(subclass) + "###" + str(contentID) + os.linesep
        indevice.writelines(line)
        indevice.close()