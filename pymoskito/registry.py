# -*- coding: utf-8 -*-

from .simulation_modules import SimulationModule, SignalMixer
from .processing_core import ProcessingModule
from .visualization import Visualizer

__all__ = ["register_simulation_module", "register_processing_module",
           "register_visualizer",
           "get_registered_modules", "get_registered_simulation_modules",
           "get_registered_processing_modules"]

"""
wrapper for easy user interaction
"""

_registry = {}


def register_module(module_cls, module_type, cls, type_check=True):
    """
    Main hook to register a class (pymoskito module) in the pymoskito framework.
    
    Args:
        module_cls (cls): Either :py:class:`pm.SimulationModule` or 
            :py:class:`pm.ProcessingModule` 
        module_type (cls): Type of the module, these are either the classes 
            listed in `simulation_modules.py`, 
            :py:class:`pm.PostProcessingModule` or 
            :py:class:`pm.MetaProcessingModule` .
        cls (cls): Class to be registered.
        type_check (bool): Perform type checking (defaults to True)
     
    Raises:
        TypeError: If `cls` is not a subclass of `module_type` .
        ValueError: If `cls` is already registered for `module_type` .

    """
    if type_check:
        if not issubclass(cls, module_type):
            raise TypeError("Module must match Type to be registered for "
                            "{0} <> {1}".format(cls, module_type))

    cls_entry = _registry.get(module_cls, {})
    entry = cls_entry.get(module_type, [])
    increment = (cls, cls.__name__)
    if increment in entry:
        raise ValueError("class {} already registered for module "
                         "{}!".format(cls, module_cls))

    entry.append(increment)

    cls_entry[module_type] = entry
    _registry[module_cls] = cls_entry

    cls_entry[module_type.__name__] = entry
    _registry[module_cls.__name__] = cls_entry


def get_registered_modules(module_cls, module_type):
    """
    Return registered classes of a module type for a specific module class.
    
    Args:
        module_cls (cls): Either :py:class:`pm.SimulationModule` or 
            :py:class:`pm.ProcessingModule` 
        module_type (cls): Type of the module, these are either the classes 
            listed in `simulation_modules.py`, 
            :py:class:`pm.PostProcessingModule` or
            :py:class:`pm.MetaProcessingModule` .
            
    Returns:
        list: List of (obj, string) tuples.
    """
    return _registry.get(module_cls, {}).get(module_type, [])


def get_module_class_by_name(module_cls, module_type, module_name):
    """
    return class object for given name
    :param module_name:
    :param module_type:
    :param module_cls:
    """
    return next((mod[0] for mod in get_registered_modules(module_cls,
                                                          module_type)
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
        if not (issubclass(module_type, SignalMixer)
                and issubclass(cls, SignalMixer)):
            raise TypeError("Class must be instance of {0}".format(module_type))

    register_module(SimulationModule, module_type, cls, type_check=False)


def get_registered_simulation_modules(module_type):
    """
    main hook to retrieve registered classes for a specific simulation module
    :param module_type:
    :return:
    """
    return get_registered_modules(SimulationModule, module_type)


def get_simulation_module_class_by_name(module_type, module_name):
    """
    Return the class of a certain simulation module given its registered name.
    
    Args:
        module_type (cls): Type of the module, 
            see :py:func:`register_simulation_module` .
        module_name (str): name of the module. 

    Returns:

    """
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
        raise TypeError("Module must match type to be registered for! "
                        "{0} <> {1}".format(vis_cls, Visualizer))

    cls_entry = _registry.get(Visualizer, [])
    increment = (vis_cls, vis_cls.__name__)
    if increment in cls_entry:
        raise ValueError("class {0} already registered as visualizer!"
                         "".format(vis_cls))

    cls_entry.append(increment)
    _registry[Visualizer] = cls_entry
    _registry[Visualizer.__name__] = cls_entry


def get_registered_visualizers():
    """
    hook to retrieve registered visualizers
    :return: visualizer class
    """
    return _registry.get(Visualizer, [])
