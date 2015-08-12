__author__ = 'stefan'

from PyQt4 import QtGui, QtCore
from pymoskito.simulation_gui import SimulationGui
import model
import control
import visualization
from visualization import BallBeamVisualizer

# create gui
app = QtGui.QApplication([])
gui = SimulationGui()
gui.show()

# add self defined visualizer
vis = BallBeamVisualizer(gui.vtk_renderer)
gui.set_visualizer(vis)

# load default config
gui.load_regimes_from_file("default.sreg")
gui.apply_regime_by_name("test-nonlinear")
# gui.start_simulation()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
