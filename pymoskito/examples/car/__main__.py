# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

    if __package__ is None or __package__ == '':
        import car
        __package__ = "car"

    app = QApplication([])
    sim = pm.Simulator()
    sim.load_regimes_from_file(os.path.join(parent_dir, "car", "default.sreg"))
    sim.apply_regime_by_name("test")
    sim.show()

    app.exec_()
