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

    # create Simulator
    sim = Simulator()

    # add self defined visualizer
    vis = TwoPendulumVisualizer(sim.vtk_renderer)
    sim.set_visualizer(vis)

    # load default config
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")
    # sim.start_simulation()

    sim.show()
    app.exec_()
