__author__ = 'stefan'

from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from PyQt4.QtCore import QObject, pyqtWrapperType


class SimulationModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class SimulationException(Exception):
    pass


class SimulationModule(QObject):
    """ Smallest Unit in Simulation Process.
        Provides necessary functions like output calculation and holds
        all settings is 'settings' all available settings have to be added
        to this dict and have to be known a priori.
    """
    __metaclass__ = SimulationModuleMeta

    def __init__(self, settings):
        QObject.__init__(self, None)
        assert isinstance(settings, OrderedDict)
        assert ("tick divider" in settings)
        self._settings = settings

    @abstractproperty
    def public_settings(self):
        pass

    @property
    def tick_divider(self):
        return self._settings["tick divider"]

    @abstractmethod
    def calc_output(self, input_vector):
        pass


class ModelException(SimulationException):
    pass


class Model(SimulationModule):
    """
    Base class for all user defined system models in state-space form.
    To be used in the simulation loop the user has the specify certain
    parameters of his implementation. See assertions in _init__
    """

    def __init__(self, settings):
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)
        assert ("state_count" in settings)
        assert ("initial state" in settings)

    @property
    def initial_state(self):
        return self._settings["initial state"]

    @abstractmethod
    def state_function(self, t, x, args):
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


class SolverException(SimulationException):
    pass


class Solver(SimulationModule):
    """
    Base Class for solver implementations
    """

    def __init__(self, settings):
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)
        assert ("Model" in settings)
        assert isinstance(settings["Model"], Model)
        self._model = settings["Model"]

    def calc_output(self, input_vector):
        self.set_input(input_vector["Controller"])
        output = self.integrate(input_vector["time"])
        try:
            self._model.check_consistency(output)
        except ModelException as e:
            raise SolverException("Timestep Integration failed! Model raised: {0}".format(e.message))
        return output

    @abstractmethod
    def set_input(self, *args):
        pass

    @abstractmethod
    def integrate(self, t):
        pass

    @abstractproperty
    def t(self):
        pass


class ControllerException(SimulationException):
    pass


class Controller(SimulationModule):
    """
    Base class for all user defined controllers
    Use input_order to define order of needed derivatives from trajectory generator
    """
    # selectable input sources for controller
    input_sources = ["system_state", "system_output", "observer"]

    def __init__(self, settings):
        SimulationModule.__init__(self, settings)
        assert ("input_order" in settings)
        assert ("input_type" in settings)
        assert (settings["input_type"] in self.input_sources)

    @property
    def input_order(self):
        return self._settings["input_order"]

    def calc_output(self, input_dict):
        input_values = next((input_dict[src] for src in self.input_sources if src == self._settings["input_type"]),
                            None)
        if input_values is None:
            raise ControllerException("Selected Input not available")

        desired_values = input_dict["Trajectory"]
        return self._control(input_values, desired_values)

    @abstractmethod
    def _control(self, is_values, desired_values):
        """
        placeholder for control law, for more sophisticated implementations
        overload calc_output.
        :param is_values: input vector of values
        :param desired_values: desired values
        :return: control output
        """
        pass


class TrajectoryException(SimulationException):
    pass


class Trajectory(SimulationModule):
    """
    Base class for all trajectory generators
    """

    def __init__(self, settings):
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)
        assert ("differential_order" in settings)

    def calc_output(self, input_vector):
        desired = self._desired_values(input_vector["time"])
        return desired

    @abstractmethod
    def _desired_values(self, t):
        pass
