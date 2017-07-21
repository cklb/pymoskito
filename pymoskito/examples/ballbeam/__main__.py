# -*- coding: utf-8 -*-
import sys
import os
import importlib
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

if __name__ == '__main__':
    # This part lets us execute this example with:
    #  $python -m pymoskito.examples.name
    pkg_path = os.path.dirname(os.path.abspath(__file__))
    pkg_name = pkg_path.split(os.path.sep)[-1]
    parent_dir = os.path.dirname(pkg_path)
    sys.path.insert(0, parent_dir)

    if __package__ is None or __package__ == '':
        importlib.import_module(pkg_name)
        __package__ = pkg_name

    # create an Application instance (needed)
    app = QApplication([])
    prog = None

    if 1:
        # create simulator
        prog = pm.SimulationGui()

        # load default config
        prog.load_regimes_from_file(os.path.join(parent_dir,
                                                 pkg_name,
                                                 "default.sreg"))
        prog.apply_regime_by_name("test-nonlinear")
    else:
        prog = pm.PostProcessor()

    # show gui
    prog.show()

    app.exec_()
