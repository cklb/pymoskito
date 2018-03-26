# -*- coding: utf-8 -*-
import pymoskito as pm

# import custom modules
import model
import controller
import visualizer_mpl
# import visualizer_vtk


if __name__ == '__main__':
    # register model
    pm.register_simulation_module(pm.Model, model.PendulumModel)

    # register controller
    pm.register_simulation_module(pm.Controller, controller.BasicController)

    # register visualizer
    pm.register_visualizer(visualizer_mpl.MplPendulumVisualizer)
    # pm.register_visualizer(visualizer_vtk.VtkPendulumVisualizer)

    # start the program
    pm.run()
