#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mainwindow import *
import sys
from PyQt4 import QtCore, QtGui

if __name__ == "__main__":
    codec = QtCore.QTextCodec.codecForName("System")
    QtCore.QTextCodec.setCodecForCStrings(codec)
    QtCore.QTextCodec.setCodecForLocale(codec)
    QtCore.QTextCodec.setCodecForTr(codec)

    trans = QtCore.QTranslator()
    trans.load("langs/zh_CN.qm")
    qtTrans = QtCore.QTranslator()
    qtTrans.load("langs/qt_zh_CN.qm")
    
    app = QtGui.QApplication(sys.argv)
    app.installTranslator(trans)
    app.installTranslator(qtTrans)
    mainwindow = CMainWindow()
    mainwindow.show()
    app.exec_()