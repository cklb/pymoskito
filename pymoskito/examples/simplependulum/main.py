# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QApplication
import numpy as np

np.seterr(all="raise")

import pymoskito as pm

if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(parent_dir)
    sys.path.insert(0, parent_dir)
    print(sys.path)

    if __package__ is None or __package__ == "":
        import simulation
        __package__ = "simulation"

    app = QApplication([])
    sim = pm.Simulator()
    sim.load_regimes_from_file(os.path.join(parent_dir, "simulation", "default.sreg"))
    sim.apply_regime_by_name("test")
    sim.show()

    app.exec_()
