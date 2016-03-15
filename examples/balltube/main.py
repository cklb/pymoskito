import sys
from PyQt4 import QtGui, QtCore
from pymoskito import Simulator, PostProcessor, \
    register_simulation_module, register_processing_module, register_visualizer, \
    Model, Controller, Feedforward, PostProcessingModule

# import self defined simulation modules
from model import BallInTubeModel, BallInTubeSpringModel
from control import ExactInputOutputLinearisation, OpenLoop
from feedforward import BallInTubeFeedforward
from visualization import BallInTubeVisualizer

from processing import ErrorProcessor


if __name__ == "__main__":
    # register Modules
    register_simulation_module(Model, BallInTubeModel)
    register_simulation_module(Model, BallInTubeSpringModel)
    register_simulation_module(Controller, ExactInputOutputLinearisation)
    register_simulation_module(Controller, OpenLoop)
    register_simulation_module(Feedforward, BallInTubeFeedforward)
    register_visualizer(BallInTubeVisualizer)

    register_processing_module(PostProcessingModule, ErrorProcessor)

    # create an Application instance (needed)
    app = QtGui.QApplication([])

    if 1:
        # create gui
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")
        sim.apply_regime_by_name("test")
        # gui.start_simulation()

        sim.show()
    else:
        post = PostProcessor()
        post.show()

    app.exec_()
