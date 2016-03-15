import sys
from PyQt4 import QtGui, QtCore
from pymoskito import Simulator, \
    register_simulation_module, register_processing_module, register_visualizer, \
    Model, Controller, Feedforward

# import self defined simulation modules
from model import BallInTubeModel, BallInTubeSpringModel
from control import ExactInputOutputLinearisation, OpenLoop
from feedforward import BallInTubeFeedforward
from visualization import BallInTubeVisualizer

from processing import ErrorProcessor

__author__ = "christoph"

if __name__ == "__main__":
    # register Modules
    register_simulation_module(Model, BallInTubeModel)
    register_simulation_module(Model, BallInTubeSpringModel)
    register_simulation_module(Controller, ExactInputOutputLinearisation)
    register_simulation_module(Controller, OpenLoop)
    register_simulation_module(Feedforward, BallInTubeFeedforward)
    register_visualizer(BallInTubeVisualizer)

    app = QtGui.QApplication([])

    # create gui
    sim = Simulator()

    # load default config
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")
    # gui.start_simulation()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        sim.show()
        QtGui.QApplication.instance().exec_()
