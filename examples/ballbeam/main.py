# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

from pymoskito import Simulator, PostProcessor,\
    register_simulation_module, register_processing_module, register_visualizer, \
    PostProcessingModule, \
    Model, Controller

from model import BallBeamModel
from control import FController
from visualization import BallBeamVisualizer
from postprocessing import EvalA1

__author__ = 'stefan'

if __name__ == '__main__':
    # register own modules
    register_simulation_module(Model, BallBeamModel)
    register_simulation_module(Controller, FController)
    register_processing_module(PostProcessingModule, EvalA1)
    register_visualizer(BallBeamVisualizer)

    app = QtGui.QApplication([])

    if 0:
        # create simulator
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")
        sim.apply_regime_by_name("test-nonlinear")
        sim.start_simulation()

        sim.show()
        QtGui.QApplication.instance().exec_()

    else:
        post = PostProcessor()
        post.show()
        QtGui.QApplication.instance().exec_()
