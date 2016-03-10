import sys
from PyQt4 import QtGui, QtCore
from pymoskito import Simulator

# import self defined simulation modules
import model
import control
import feedforward
import processing
from visualization import BallInTubeVisualizer

__author__ = 'christoph'

if __name__ == '__main__':
    app = QtGui.QApplication([])

    # create gui
    sim = Simulator()

    # load default config
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")
    # gui.start_simulation()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sim.show()
        QtGui.QApplication.instance().exec_()
