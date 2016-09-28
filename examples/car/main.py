# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication

from .model import CarModel
from pymoskito import (Simulator, register_simulation_module, register_visualizer, Model)
from .visualization import CarVisualizer


if __name__ == '__main__':
    register_simulation_module(Model, CarModel)
    register_visualizer(CarVisualizer)

    app = QApplication([])
    sim = Simulator()
    sim.load_regimes_from_file("default.sreg")
    sim.apply_regime_by_name("test")

    sim.show()

    app.exec_()
