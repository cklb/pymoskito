# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

from pymoskito import Simulator, PostProcessor
import model
import control
import visualization

__author__ = 'stefan'


if __name__ == '__main__':
    app = QtGui.QApplication([])

    # create simulator
    sim = Simulator()

    # load default config
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test-nonlinear")
    sim.start_simulation()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sim.show()
        QtGui.QApplication.instance().exec_()
