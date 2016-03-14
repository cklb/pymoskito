# -*- coding: utf-8 -*-
from PyQt4.QtGui import QApplication
from pymoskito import Simulator, PostProcessor

# import custom simulation modules
import model
import control
from visualization import TwoPendulumVisualizer

__author__ = 'christoph'

if __name__ == '__main__':
    # create an Application instance (needed)
    app = QApplication([])

    if 1:
        # create Simulator
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")

        # apply a regime
        sim.apply_regime_by_name("test")

        # remote start a simulation
        # sim.start_simulation()

        sim.show()
    else:
        post = PostProcessor()
        post.show()

    app.exec_()
