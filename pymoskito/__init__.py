# -*- coding: utf-8 -*-
import logging.config
import os

import matplotlib as mpl
import yaml

# make everybody use qt5
mpl.use('Qt5Agg')
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

from .registry import *
from .generic_processing_modules import *
from .generic_simulation_modules import *
from .processing_core import *
from .processing_gui import *
from .simulation_gui import *
from .simulation_modules import *
from .tools import *
from .controltools import *
from .visualization import *

__author__ = 'Stefan Ecklebe'
__email__ = 'stefan.ecklebe@tu-dresden.de'
__version__ = '0.2.0'

# configure logging
with open(get_resource("logging.yaml", ""), "r") as f:
    log_conf = yaml.load(f)

logging.config.dictConfig(log_conf)

# register all generic modules
register_simulation_module(Model, LinearStateSpaceModel)
register_simulation_module(Solver, ODEInt)
register_simulation_module(Trajectory, SmoothTransition)
register_simulation_module(Trajectory, HarmonicTrajectory)
register_simulation_module(Trajectory, Setpoint)
register_simulation_module(Controller, PIDController)
register_simulation_module(Controller, LinearStateSpaceController)
register_simulation_module(ModelMixer, AdditiveMixer)
register_simulation_module(ObserverMixer, AdditiveMixer)
register_simulation_module(Limiter, ModelInputLimiter)
register_simulation_module(Sensor, DeadTimeSensor)
register_simulation_module(Disturbance, GaussianNoise)

register_processing_module(PostProcessingModule, StepResponse)
register_processing_module(PostProcessingModule, PlotAll)
