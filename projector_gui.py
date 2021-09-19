#!/usr/bin/env python3

import sys

from pypjlink import Projector, MUTE_VIDEO

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

import threading
import datetime
import time

import queue

ProjAddrs = {'StageLeft' : 'ch-proj1.pius.org',
             'StageRight': 'ch-proj3.pius.org',
             'Center'    : 'ch-proj2.pius.org'}

class ProjectorInterface(QThread):

    powerUpdated = pyqtSignal(str)
    timeUpdated = pyqtSignal(str)

    def __init__(self, name, addr, parent=None):
        super(ProjectorInterface, self).__init__(parent)

        self.name = name
        self._addr = addr
        self.queue = queue.SimpleQueue()

    @pyqtSlot()
    def powerOn(self):
        self.queue.put(True)

    @pyqtSlot()
    def powerOff(self):
        self.queue.put(False)

    def run(self):
        proj = None

        last = time.time()

        while True:

            if proj is None:
                proj = Projector.from_address(addr)
                proj.authenticate('admin')

            try:
                if self.queue.empty() is False:
                    st = self.queue.get_nowait()

                    if st:
                        proj.set_power('on')
                    else:
                        proj.set_power('off')

                    continue

                self.powerUpdated.emit(proj.get_power())
                self.timeUpdated.emit(str(datetime.datetime.now()))
            except Exception as e:
                print(f"Got message error {e}")
                proj = None

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

            dtime = QLineEdit()
            dtime.setReadOnly(True)
            self.projs[i].timeUpdated.connect(dtime.setText)
            fl.addRow(k + ' Last:',dtime)

        powerOnBtn = QPushButton("Power All On")
        powerOnBtn.pressed.connect(self.projs[0].powerOn)
        powerOnBtn.pressed.connect(self.projs[1].powerOn)
        powerOnBtn.pressed.connect(self.projs[2].powerOn)
        fl.addRow("",powerOnBtn)

        powerOffBtn = QPushButton("Power All Off")
        powerOffBtn.pressed.connect(self.projs[0].powerOff)
        powerOffBtn.pressed.connect(self.projs[1].powerOff)
        powerOffBtn.pressed.connect(self.projs[2].powerOff)
        fl.addRow("",powerOffBtn)

        for p in self.projs:
            p.start()

        self.resize(400,300)


appTop = QApplication(sys.argv)

gui = ProjectorControl()
gui.show()
appTop.exec_()

