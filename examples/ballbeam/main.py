__author__ = 'stefan'

from PyQt4 import QtGui, QtCore
from pymoskito.simulation_gui import SimulationGui

# import self defined simulation modules
from model import BallBeamModel
from visualization import BallBeamVisualizer

# create gui
app = QtGui.QApplication([])
gui = SimulationGui()

# add self defined visualizer
vis = BallBeamVisualizer(gui.vtk_renderer)
gui.set_visualizer(vis)

gui.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
