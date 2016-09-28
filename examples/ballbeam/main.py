# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
from pymoskito import Simulator, PostProcessor, \
    register_simulation_module, register_processing_module, register_visualizer, \
    PostProcessingModule, \
    Model, Controller

from control import FController
from model import BallBeamModel
from postprocessing import EvalA1
from visualization import BallBeamVisualizer

if __name__ == '__main__':
    # register own modules
    register_simulation_module(Model, BallBeamModel)
    register_simulation_module(Controller, FController)
    register_processing_module(PostProcessingModule, EvalA1)
    register_visualizer(BallBeamVisualizer)

    # create an Application instance (needed)
    app = QApplication([])

    if 0:
        # create simulator
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")
        sim.apply_regime_by_name("test-nonlinear")
        sim.start_simulation()

        sim.show()
        QApplication.instance().exec_()

    else:
        post = PostProcessor()
        post.show()

    app.exec_()
