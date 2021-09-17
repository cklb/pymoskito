# -*- coding: utf-8 -*-
import logging.config
import os
import yaml

# make all plotting libs use qt5
import matplotlib as mpl
mpl.use('Qt5Agg')
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

# enable high dpi scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from .registry import *

from .processing_core import *
from .processing_gui import *
from .generic_processing_modules import *

from .simulation_gui import *
from .simulation_modules import *
from .generic_simulation_modules import *

from .binding_modules import *

from .tools import *
from .controltools import *
from .visualization import *
from .resources import *

__author__ = 'Stefan Ecklebe'
__email__ = 'stefan.ecklebe@tu-dresden.de'
__version__ = '0.4.0rc4'

# configure logging
with open(get_resource("logging.yaml", ""), "r") as f:
    log_conf = yaml.full_load(f)

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

register_processing_module(PostProcessingModule, PlotAll)
