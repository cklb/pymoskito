# -*- coding: utf-8 -*-
from simulation_gui import SimulationGui as Simulator
from processing_gui import PostProcessor as PostProcessor
from simulation_modules import Model, Controller, Feedforward
from processing_core import PostProcessingModule, MetaProcessingModule
from registry import register_simulation_module, register_processing_module, register_visualizer,\
    get_registered_simulation_modules, get_registered_processing_modules

import yaml
import logging.config
from tools import get_resource

__author__ = 'Stefan Ecklebe'
__email__ = 'stefan.ecklebe@tu-dresden.de'
__version__ = '0.1.0'


with open(get_resource("logging.yaml", ""), "r") as f:
    log_conf = yaml.load(f)

logging.config.dictConfig(log_conf)
# logging.config.fileConfig(get_resource("logging.conf", ""))
