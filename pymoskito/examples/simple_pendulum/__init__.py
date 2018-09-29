from . import model
from . import controller
from . import visualizer_mpl
# from . import visualizer_vtk

import pymoskito as pm

# register model
pm.register_simulation_module(pm.Model, model.PendulumModel)

# register controller
pm.register_simulation_module(pm.Controller, controller.BasicController)

# register visualizer
pm.register_visualizer(visualizer_mpl.MplPendulumVisualizer)
# pm.register_visualizer(visualizer_vtk.VtkPendulumVisualizer)
