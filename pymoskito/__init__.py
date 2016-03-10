# -*- coding: utf-8 -*-
from simulation_gui import SimulationGui as Simulator
from processing_gui import PostProcessor as PostProcessor
from registry import register_simulation_module, register_processing_module, get_registered_simulation_modules, \
    get_registered_processing_modules, register_visualizer

import logging.config
from tools import get_resource

__author__ = 'Stefan Ecklebe'
__email__ = 'stefan.ecklebe@tu-dresden.de'
__version__ = '0.1.0'

logging.config.fileConfig(get_resource("logging.conf", ""))
