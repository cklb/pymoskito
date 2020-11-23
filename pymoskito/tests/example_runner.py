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
    orig_dir = os.path.dirname(__file__)
    ex_dir = os.sep.join([orig_dir, os.pardir, "examples", name])
    res_dir = os.sep.join([orig_dir, "results", name])
    os.makedirs(res_dir, exist_ok=True)
    os.chdir(os.path.abspath(ex_dir))

    app = QApplication([])
    gui = pm.SimulationGui()
    gui.load_regimes_from_file("default.sreg")
    gui.actExitOnBatchCompletion.setChecked(True)
    gui._settings.setValue("path/simulation_results", os.path.abspath(res_dir))
    gui.start_regime_execution()

    os.chdir(orig_dir)
    app.exec_()
