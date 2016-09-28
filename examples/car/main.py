# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
from pymoskito import (Simulator, register_simulation_module, register_visualizer, Model)

from visualization import CarVisualizer
from model import CarModel

if __name__ == '__main__':
    register_simulation_module(Model, CarModel)
    register_visualizer(CarVisualizer)

    app = QApplication([])
    sim = Simulator()
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")
    # sim.start_simulation()
    # sim.shortSaveResult
    sim.show()

    app.exec_()
