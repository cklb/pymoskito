"""
Simple script that runs a pymoksito example

The name of the example must be given as first argument
"""

import sys
import os
from importlib import import_module
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

if __name__ == '__main__':
    name = sys.argv[1]
    import_module("pymoskito.examples." + name)

    app = QApplication([])
    gui = pm.SimulationGui()
    mod_dir = os.path.dirname(__file__)
    gui.load_regimes_from_file(os.sep.join([os.path.dirname(__file__),
                                            "..",
                                            "examples",
                                            name,
                                            "default.sreg"]))
    gui.actExitOnBatchCompletion.setChecked(True)
    gui._settings.setValue("path/simulation_results",
                           os.path.abspath(os.curdir))
    gui.start_regime_execution()
    app.exec_()
