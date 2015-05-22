__author__ = 'stefan'

from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from PyQt4.QtCore import QObject, pyqtWrapperType


class SimulationModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class SimulationModule(QObject):
    """ Smallest Unit in Simulation Process.
        Provides necessary functions like output calculation and holds
        all settings is 'settings' all available settings have to be added
        to this dict and have to be known a priori.
    """
    __metaclass__ = SimulationModuleMeta

    def __init__(self, parent=None, settings=None):
        QObject.__init__(self, parent)
        assert isinstance(settings, OrderedDict)
        self.settings = settings

    @abstractproperty
    def mandatory_settings(self):
        pass

    @abstractproperty
    def public_settings(self):
        pass

    @abstractproperty
    def output_dim(self):
        return 0

    @abstractmethod
    def calc_output(self):
        pass


class ModelException(Exception):
    pass


class Model(SimulationModule):
    """
    Base class for all user defined system models in state-space form.
    To be used in the simulation loop the user has the specify certain
    parameters of his implementation. See assertions in _init__
    """

    def __init__(self, settings):
        """
        """
        SimulationModule.__init__(self)
        assert("state_count" in settings)
        self._settings = settings

    def mandatory_settings(self):
        return list("state_count")

    def output_dim(self):
        return self._private_settings["state_count"]

    def calc_output(self):
        """
        Not needed for models, since they get wrapped by solver zo compute
        output values.
        :return: None
        """
        return None

    @abstractmethod
    def state_function(self, x, t, *args):
        """
        function that calculates the state derivatives of a system with state x at time t.
        :param x: system state
        :param t: system time
        :return: derivatives of system state at time t
        """
        pass

    @abstractmethod
    def root_function(self, x):
        """
        function that signal the integrator when a reinitialisation should be performed
        due to discontinuities in the model equations.
        :param x: system state
        :return: True if reset is advised
        """
        return False

    @abstractmethod
    def check_consistency(self, x):
        """
        checks whether the assumptions, made in the modelling process are violated.
        :param x: system state
        :raises: ModelException if violation is detected
        """
        pass
