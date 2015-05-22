__author__ = 'stefan'

from abc import ABCMeta, abstractmethod
import vtk


class Visualizer:
    """
    Base Class with some function the help visualizing the system using vtk
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def update_scene(self, x):
        """
        Hook to update the current visualization state
        :param x: system state vector
        """
        pass
