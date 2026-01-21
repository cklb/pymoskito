# -*- coding: utf-8 -*-
import sys
import os
import importlib
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

import model
import controller
import visualization
import postprocessing

if __name__ == '__main__':

    pm.register_simulation_module(pm.Model, model.ReducedBalanceBoardModel)
    pm.register_simulation_module(pm.Model, model.ReducedBalanceBoardModelParLin)
    pm.register_simulation_module(pm.Model, model.BalanceBoardModel)
    pm.register_simulation_module(pm.Model, model.BalanceBoardModelParLin)
    pm.register_simulation_module(pm.Model, model.SymbolicBalanceBoardModel)
    pm.register_simulation_module(pm.Controller, controller.BBLinearController)
    pm.register_simulation_module(pm.Controller, controller.BBGainSchedulingController)
    pm.register_visualizer(visualization.BalanceBoard3DVisualizer)
    pm.register_visualizer(visualization.BalanceBoard2DVisualizer)
    pm.register_processing_module(pm.PostProcessingModule, postprocessing.SimpleBalanceBoardPostProcessor)
    pm.register_processing_module(pm.PostProcessingModule, postprocessing.ComparisonBalanceBoardPostProcessor)

    
    # path magic
    pkg_path = os.path.dirname(os.path.abspath(__file__))
    pkg_name = pkg_path.split(os.path.sep)[-1]
    parent_dir = os.path.dirname(pkg_path)
    sys.path.insert(0, parent_dir)
    
    if __package__ is None or __package__ == '':
        importlib.import_module(pkg_name)
        __package__ = pkg_name

    app = QApplication([])
    prog = pm.SimulationGui()
    prog.load_regimes_from_file(os.path.join(parent_dir,pkg_name,"default.sreg"))
    prog.show()
    app.exec_()