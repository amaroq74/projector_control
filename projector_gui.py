#!/usr/bin/env python3

import sys

from pypjlink import Projector, MUTE_VIDEO

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

ProjAddrs = {'StageLeft' : 'ch-proj1.pius.org',
             'StageRight': 'ch-proj3.pius.org',
             'Center'    : 'ch-proj2.pius.org'}

class ProjectorControl(QWidget):

    # Field update signals
    updatePowerStatus   = [pyqtSignal(str)] * len(ProjAddrs)
    updateShutterStatus = [pyqtSignal(str)] * len(ProjAddrs)

    def __init__(self, parent=None):
        super(ProjectorControl, self).__init__(parent)

        self.thread = threading.Thread(target=self.pollStatus)
        self.thread.start()

        self.projs = [Projector.from_address(v) for k,v in ProjAddrs.items()]

        for p in self.projs:
            p.authenticate('admin')

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

            power = QLineEdit()
            power.setReadOnly(True)
            self.updatePowerStatus[i].connect(power.setText)
            fl.addRow(v + ' Power:',power)

            shutter = QLineEdit()
            shutter.setReadOnly(True)
            self.updateShutterStatus[i].connect(shutter.setText)
            fl.addRow(v + ' Shutter:',shutter)

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

        self.resize(500,600)

    @pyqtSlot()
    def powerOnPressed(self):
        pass

    @pyqtSlot()
    def powerOffPressed(self):
        pass

    def pollStatus(self):

        while(True):

            for p in self.projs:
                self.updatePowerStatus.emit(p.get_power())
                self.updateShutterStatus.emit(p.get_mute()[0])


appTop = QApplication(sys.argv)

gui = gui.ProjectorControl()
gui.show()
appTop.exec_()

