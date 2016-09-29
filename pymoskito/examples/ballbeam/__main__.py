# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

    if __package__ is None or __package__ == '':
        import ballbeam
        __package__ = "ballbeam"

    # create an Application instance (needed)
    app = QApplication([])
    prog = None

    if 0:
        # create simulator
        prog = pm.Simulator()

        # load default config
        prog.load_regimes_from_file(os.path.join(parent_dir, "ballbeam", "default.sreg"))
        prog.apply_regime_by_name("test-nonlinear")
    else:
        prog = pm.PostProcessor()

    # show gui
    prog.show()

    app.exec_()
