# -*- coding: utf-8 -*-
from PyQt4.QtGui import QApplication

from pymoskito import Simulator, PostProcessor, \
    register_simulation_module, register_processing_module, register_visualizer, \
    PostProcessingModule, \
    Model, Controller

from model import CarModel
from visualization import CarVisualizer


if __name__ == '__main__':
    register_simulation_module(Model, CarModel)
    register_visualizer(CarVisualizer)

    app = QApplication([])
    sim = Simulator()
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")

    sim.show()

    app.exec_()
