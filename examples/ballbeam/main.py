__author__ = 'stefan'

from PyQt4 import QtGui, QtCore
from pymoskito.simulation_gui import SimulationGui

# import self defined simulation modules
from model import BallBeamModel
from visualization import BallBeamVisualizer

# create gui
app = QtGui.QApplication([])
gui = SimulationGui()
gui.show()

# add self defined visualizer
vis = BallBeamVisualizer(gui.renderer)
gui.set_visualizer(vis)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
