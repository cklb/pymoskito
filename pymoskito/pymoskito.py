# -*- coding: utf-8 -*-
from __future__ import division
from simulation_modules import SimulationModule, SignalMixer
"""
wrapper for easy user interaction
"""

_registry = {}

def register_simulation_module(module_type, cls):
    """
    main hook to register a class in the pymoskito framework
    :param cls: class to be registered
    :return: None
    """
    if not issubclass(cls, SimulationModule):
        raise TypeError("Only Simulation Modules can be registered!")
    if not issubclass(cls, module_type):
        # more complex inheritance allowed for mixers
        if not (issubclass(module_type, SignalMixer) and issubclass(cls, SignalMixer)):
            raise TypeError("Class must be instance of {0}!".format(module_type))

    # add class to corresponding type
    entry = _registry.get(module_type, [])
    # TODO check for duplicates
    entry.append(cls)
    _registry[module_type] = entry

def get_registered_modules(module_type):
    """
    main hook to retrieve registered classes for a specific simulation module
    :param module_type:
    :return:
    """
    return _registry.get(module_type, [])
