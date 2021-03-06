#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mainwindow_ui import *
from config import *
from updater import *
from PyQt4 import QtGui
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
import os
import time

class CMainWindow(QtGui.QWidget):
    updaters = []
    sendmsg = QtCore.pyqtSignal(str, str)
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        DBusGMainLoop(set_as_default = True)
        self.bus = dbus.SystemBus()
        self.proxy = self.bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
        self.iface = dbus.Interface(self.proxy, "org.freedesktop.UDisks")
        self.iface.connect_to_signal('DeviceChanged', self.deviceInserted)
        self.iface.connect_to_signal('DeviceRemoved', self.deviceRemoved)
        self.running = False
        self.ui.startButton.clicked.connect(self.start, QtCore.Qt.QueuedConnection)
        self.sendmsg[str, str].connect(self.message, QtCore.Qt.QueuedConnection)
        
    def start(self):
        if self.running == False:
            self.ui.statusLabel.setText(QtGui.QApplication.translate('mainWindow', 'System is running'))
            self.ui.startButton.setText(QtGui.QApplication.translate('mainWindow', 'Stop'))
            self.running = True
            msg = QtGui.QApplication.translate('mainWindow', "System started")
            self.sendmsg.emit(msg, "red")

        else:
            self.ui.statusLabel.setText(QtGui.QApplication.translate('mainWindow', 'System is stopped'))
            self.ui.startButton.setText(QtGui.QApplication.translate('mainWindow', 'Start'))
            self.running = False
            msg = QtGui.QApplication.translate('mainWindow', "System stopped")
            self.sendmsg.emit(msg, "red")

    def deviceInserted(self, device):
        if self.running == False:
            return 

        deviceObj = self.bus.get_object("org.freedesktop.UDisks", device)
        deviceProps = dbus.Interface(deviceObj, dbus.PROPERTIES_IFACE)
        
        try:
            mountPath = deviceProps.Get('org.freedesktop.UDisks.Device', "DeviceMountPaths")[0]
            serial = deviceProps.Get('org.freedesktop.UDisks.Device', "DriveSerial")
        except IndexError:
            return

        root = mountPath + USER_ROOT
        if not os.path.exists(root):
            return

        msg = QtGui.QApplication.translate('mainWindow', "Device(%1) inserted").arg(serial)
        self.sendmsg.emit(msg, "red")
        updater = CUpdater(self, deviceObj)
        self.updaters.append(updater)
        updater.sendmsg[str, str].connect(self.message, QtCore.Qt.QueuedConnection)
        updater.finished[dbus.String, dbus.proxies.ProxyObject].connect(self.finished, QtCore.Qt.QueuedConnection)
        updater.setNames(root, serial)
        updater.start()

    def deviceRemoved(self, device):
        pass

    def finished(self, serial, deviceObj):
        devIfce = dbus.Interface(deviceObj, 'org.freedesktop.UDisks.Device')
        devIfce.FilesystemUnmount([])
        msg = QtGui.QApplication.translate('mainWindow', "Device(%1) is unmounted").arg(serial)
        self.sendmsg.emit(msg, "red")

    @QtCore.pyqtSlot(str, str)
    def message(self, msg, msgType):
        timeMsg = time.ctime()
        if msgType == "blue":
            msg = "<font color=blue>" + "[" + timeMsg + "]" + "  " + msg + "</font>"
        elif msgType == "red":
            msg = "<font color=red>" + "[" + timeMsg + "]" + "  " + msg + "</font>"
        else:
            msg = "[" + timeMsg + "]" + "  " + msg
        self.ui.messages.append(msg)