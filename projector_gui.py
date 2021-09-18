#!/usr/bin/env python3

import sys

from pypjlink import Projector, MUTE_VIDEO

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

import threading
import datetime
import time

ProjAddrs = {'StageLeft' : 'ch-proj1.pius.org',
             'StageRight': 'ch-proj3.pius.org',
             'Center'    : 'ch-proj2.pius.org'}

class ProjectorInterface(QThread):

    powerUpdated = pyqtSignal(str)
    shutterUpdated = pyqtSignal(str)
    timeUpdated = pyqtSignal(str)

    def __init__(self, name, addr, parent=None):
        super(ProjectorInterface, self).__init__(parent)

        self.name = name
        self._addr = addr
        self.proj = Projector.from_address(addr)
        self.proj.authenticate('admin')

    def powerOn(self):
        self.proj.set_power('on')

    def powerOff(self):
        self.proj.set_power('off')

    def shutterOn(self):
        self.proj.set_mute(MUTE_VIDEO,True)

    def shutterOff(self):
        self.proj.set_mute(MUTE_VIDEO,False)

    def run(self):
        last = time.time()

        while True:
            self.powerUpdated.emit(self.proj.get_power())
            self.shutterUpdated.emit(str(self.proj.get_mute()))
            self.timeUpdated.emit(str(datetime.datetime.now()))

            dur = time.time() - last

            if dur < 1.0:
                time.sleep(1.0-dur)

            last = time.time()

class ProjectorControl(QWidget):

    updateTime = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProjectorControl, self).__init__(parent)

        self.projs = [None] * len(ProjAddrs)

        self.setWindowTitle("St. Pius Projector Control")

        # Setup status widgets
        top = QVBoxLayout()
        self.setLayout(top)

        fl = QFormLayout()
        fl.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        top.addLayout(fl)

        for i, (k,v) in enumerate(ProjAddrs.items()):
            self.projs[i] = ProjectorInterface(k,v,self)

            power = QLineEdit()
            power.setReadOnly(True)
            self.projs[i].powerUpdated.connect(power.setText)
            fl.addRow(k + ' Power:',power)

            shutter = QLineEdit()
            shutter.setReadOnly(True)
            self.projs[i].shutterUpdated.connect(shutter.setText)
            fl.addRow(k + ' Shutter:',shutter)

            dtime = QLineEdit()
            dtime.setReadOnly(True)
            self.projs[i].timeUpdated.connect(dtime.setText)
            fl.addRow(k + ' Last:',dtime)

        powerOnBtn = QPushButton("Power All On")
        powerOnBtn.pressed.connect(self.powerOnPressed)
        fl.addRow("",powerOnBtn)

        powerOffBtn = QPushButton("Power All Off")
        powerOffBtn.pressed.connect(self.powerOffPressed)
        fl.addRow("",powerOffBtn)

        shutterOnBtn = QPushButton("Shutter All On")
        shutterOnBtn.pressed.connect(self.shutterOnPressed)
        fl.addRow("",shutterOnBtn)

        shutterOffBtn = QPushButton("Shutter All Off")
        shutterOffBtn.pressed.connect(self.shutterOffPressed)
        fl.addRow("",shutterOffBtn)

        for p in self.projs:
            p.start()

        self.resize(500,600)

    @pyqtSlot()
    def powerOnPressed(self):
        for p in self.projs:
            p.powerOn()

    @pyqtSlot()
    def powerOffPressed(self):
        for p in self.projs:
            p.powerOff()

    @pyqtSlot()
    def shutterOnPressed(self):
        for p in self.projs:
            p.shutterOn()

    @pyqtSlot()
    def shutterOffPressed(self):
        for p in self.projs:
            p.shutterOff()

appTop = QApplication(sys.argv)

gui = ProjectorControl()
gui.show()
appTop.exec_()

