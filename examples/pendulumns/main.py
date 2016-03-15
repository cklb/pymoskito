# -*- coding: utf-8 -*-
from PyQt4.QtGui import QApplication

from pymoskito import Simulator, PostProcessor,\
    register_simulation_module, register_processing_module, register_visualizer, \
    PostProcessingModule, \
    Model, Controller

# import custom simulation modules
from model import TwoPendulumModel, TwoPendulumModel2, TwoPendulumModelParLin
from control import LinearStateFeedback, LinearStateFeedbackParLin, CLinearStateFeedback, LjapunovController,\
    CLjapunovController, SwingUpController, SwingUpController2, CSwingUpController2
from visualization import TwoPendulumVisualizer
from processing import TwoPendulum

__author__ = 'christoph'

if __name__ == '__main__':
    # register own modules
    register_simulation_module(Model, TwoPendulumModel)
    register_simulation_module(Model, TwoPendulumModel2)
    register_simulation_module(Model, TwoPendulumModelParLin)

    register_simulation_module(Controller, LinearStateFeedback)
    register_simulation_module(Controller, LinearStateFeedbackParLin)
    register_simulation_module(Controller, CLinearStateFeedback)
    register_simulation_module(Controller, LjapunovController)
    register_simulation_module(Controller, CLjapunovController)
    register_simulation_module(Controller, SwingUpController)
    register_simulation_module(Controller, SwingUpController2)
    register_simulation_module(Controller, CSwingUpController2)

    register_visualizer(TwoPendulumVisualizer)

    register_processing_module(PostProcessingModule, TwoPendulum)

    # create an Application instance (needed)
    app = QApplication([])

    if 1:
        # create Simulator
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")

        # apply a regime
        sim.apply_regime_by_name("test")

        # remotely start a simulation
        # sim.start_simulation()

        sim.show()
    else:
        post = PostProcessor()
        post.show()

    app.exec_()
