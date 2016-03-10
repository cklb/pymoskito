# -*- coding: utf-8 -*-
from __future__ import division
from simulation_modules import SimulationModule, SignalMixer
from processing_core import ProcessingModule
from visualization import Visualizer

"""
wrapper for easy user interaction
"""

_registry = {}


def register_module(module_cls, module_type, cls, type_check=True):
    """
    main hook to register a class in the pymoskito framework
    :param module_type:
    :param module_cls:
    :param cls: class to be registered
    :param type_check: performtype checking
    :return: None
    """
    if type_check:
        if not issubclass(cls, module_type):
            raise TypeError("Module must match Type to be registered for! {0} <> {1}".format(cls, module_type))

    cls_entry = _registry.get(module_cls, {})
    entry = cls_entry.get(module_type, [])
    # TODO check for duplicates here

    entry.append((cls, cls.__name__))

    cls_entry[module_type] = entry
    _registry[module_cls] = cls_entry

    cls_entry[module_type.__name__] = entry
    _registry[module_cls.__name__] = cls_entry


def get_registered_modules(module_cls, module_type):
    """
    main hook to retrieve registered classes of a module type for a specific module class
    :param module_cls:
    :param module_type:
    :return:
    """
    return _registry.get(module_cls, {}).get(module_type, [])


def get_module_class_by_name(module_cls, module_type, module_name):
    """
    return class object for given name
    :param module_name:
    :param module_type:
    :param module_cls:
    """
    return next((mod[0] for mod in get_registered_modules(module_cls, module_type)
                 if mod[1] == module_name), None)


def register_simulation_module(module_type, cls):
    """
    main hook to register a module in the pymoskito framework
    :param module_type:
    :param cls: class to be registered
    :return: None
    """
    if not issubclass(cls, SimulationModule):
        raise TypeError("Only Simulation Modules can be registered!")
    if not issubclass(cls, module_type):
        # more complex inheritance allowed for mixers
        if not (issubclass(module_type, SignalMixer) and issubclass(cls, SignalMixer)):
            raise TypeError("Class must be instance of {0}!".format(module_type))

    register_module(SimulationModule, module_type, cls, type_check=False)


def get_registered_simulation_modules(module_type):
    """
    main hook to retrieve registered classes for a specific simulation module
    :param module_type:
    :return:
    """
    return get_registered_modules(SimulationModule, module_type)


def get_simulation_module_class_by_name(module_type, module_name):
    return get_module_class_by_name(SimulationModule, module_type, module_name)


def register_processing_module(module_type, cls):
    """
    main hook to register a class in the pymoskito framework
    :param module_type:
    :param cls: class to be registered
    :return: None
    """
    if not issubclass(cls, ProcessingModule):
        raise TypeError("Only PostProcessing Modules can be registered!")

    register_module(ProcessingModule, module_type, cls)


def get_registered_processing_modules(module_type):
    """
    main hook to retrieve registered classes for a specific simulation module
    :param module_type:
    :return:
    """
    return get_registered_modules(ProcessingModule, module_type)


def get_processing_module_class_by_name(module_type, module_name):
    return get_module_class_by_name(ProcessingModule, module_type, module_name)


def register_visualizer(vis_cls):
    """
    hook to register a visualizer for the simulation GUI

    :param vis_cls: class to be registered
    """
    if not issubclass(vis_cls, Visualizer):
        raise TypeError("Module must match type to be registered for! {0} <> {1}".format(vis_cls, Visualizer))

    cls_entry = _registry.get(Visualizer, [])
    cls_entry.append((vis_cls, vis_cls.__name__))
    _registry[Visualizer] = cls_entry
    _registry[Visualizer.__name__] = cls_entry


def get_registered_visualizers():
    """
    hook to retrieve registered visualizers
    :return: visualizer class
    """
    return _registry.get(Visualizer, [])
