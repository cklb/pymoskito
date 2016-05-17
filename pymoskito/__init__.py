# -*- coding: utf-8 -*-
import logging.config

import yaml

from generic_processing_modules import StepResponse, PlotAll, XYMetaProcessor
from generic_simulation_modules import ODEInt, SmoothTransition, HarmonicTrajectory, Setpoint, PIDController, \
    PyTrajectory, AdditiveMixer, ModelInputLimiter, DeadTimeSensor, GaussianNoise
from processing_core import PostProcessingModule, MetaProcessingModule
from processing_gui import PostProcessor as PostProcessor
from registry import register_simulation_module, register_processing_module, register_visualizer,\
    get_registered_simulation_modules, get_registered_processing_modules
from simulation_gui import SimulationGui as Simulator
from simulation_modules import Solver, Trajectory, Model, Feedforward, Controller, ModelMixer, ObserverMixer, \
    Disturbance, Sensor, Limiter
from tools import get_resource

__author__ = 'Stefan Ecklebe'
__email__ = 'stefan.ecklebe@tu-dresden.de'
__version__ = '0.1.0'


# configure logging
with open(get_resource("logging.yaml", ""), "r") as f:
    log_conf = yaml.load(f)

logging.config.dictConfig(log_conf)

# register all generic modules
register_simulation_module(Solver, ODEInt)
register_simulation_module(Trajectory, SmoothTransition)
register_simulation_module(Trajectory, HarmonicTrajectory)
register_simulation_module(Trajectory, Setpoint)
register_simulation_module(Controller, PIDController)
register_simulation_module(Feedforward, PyTrajectory)
register_simulation_module(ModelMixer, AdditiveMixer)
register_simulation_module(ObserverMixer, AdditiveMixer)
register_simulation_module(Limiter, ModelInputLimiter)
register_simulation_module(Sensor, DeadTimeSensor)
register_simulation_module(Disturbance, GaussianNoise)

register_processing_module(PostProcessingModule, StepResponse)
register_processing_module(PostProcessingModule, PlotAll)
