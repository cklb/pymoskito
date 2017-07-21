import logging
from copy import copy
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

from PyQt5.QtCore import QObject
pyqtWrapperType = type(QObject)

__all__ = ["Trajectory", "Feedforward", "Controller", "Limiter",
           "ModelMixer", "Model", "ModelException",
           "Solver", "Disturbance", "Sensor", "ObserverMixer", "Observer"]


class SimulationModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class SimulationException(Exception):
    pass


class SimulationModule(QObject, metaclass=SimulationModuleMeta):
    """
    Smallest Unit in Simulation Process.

    This class provides necessary functions like output calculation and holds
    all settings that can be accessed by the user.
    öis 'settings' all available settings have to be added
    to this dict and have to be known a priori.

    Args:
        settings(OrderedDict): Settings for this simulation module.
            These entries will be shown in the properties view and can be
            changed by the user.
    """

    def __init__(self, settings):
        QObject.__init__(self, None)
        self._logger = logging.getLogger(self.__class__.__name__)

        assert isinstance(settings, dict)
        self._settings = copy(settings)

        self._settings["tick divider"] = settings.get("tick divider", 1)
        self._settings["step width"] = None
        self._settings.pop("modules", None)

    @property
    @abstractmethod
    def public_settings(self):
        pass

    @property
    def tick_divider(self):
        return self._settings["tick divider"]

    @property
    def step_width(self):
        return self._settings["step width"]

    @step_width.setter
    def step_width(self, value):
        self._settings["step width"] = value

    @abstractmethod
    def calc_output(self, input_vector):
        pass


class ModelException(SimulationException):
    """
    Exception to be raised if the current system state violates modelling
    assumptions.
    """
    pass


class Model(SimulationModule):
    """
    Base class for all user defined system models in state-space form.

    Args:
        settings (dict): Dictionary holding the config options for this module.
            It must contain the following keys:

            `input_count`
                The length of the input vector for this model.

            `state_count`
                The length of the state vector for this model.

            `initial state`
                The initial state vector for this model.
    """

    def __init__(self, settings):
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)
        assert ("state_count" in settings)
        assert ("input_count" in settings)
        assert ("initial state" in settings)
        assert len(settings["initial state"]) == settings["state_count"]

    @property
    def initial_state(self):
        """ Return the initial state of the system. """
        return self._settings["initial state"]

    @abstractmethod
    def state_function(self, t, x, args):
        """
        Calculate the state derivatives of a system with state x at time t.

        Args:
            x(Array-like): System state.
            t(float): System time.

        Returns:
            Temporal derivative of the system state at time t.
        """
        pass

    def root_function(self, x):
        """
        Check whether a reinitialisation of the integrator should be performed.
        
        
        This can be the case if there are discontinuities in the system dynamics
        such as switching.
        
        Args:
            x(array-like): Current system state.
            
        Returns: 
            tuple: 
                * bool: `True` if reset is advised.
                * array-like: State to continue with.
                
        """
        return False, x

    def check_consistency(self, x):
        """
        Check whether the assumptions, made in the modelling process are 
        violated.
        
        Args:
            x: Current system state
            
        Raises: 
            :py:class:`ModelException` : If a violation is detected. This will
                stop the simulation process.
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
        assert isinstance(settings["modules"]["Model"], Model)
        self._model = settings["modules"]["Model"]
        self.next_output = None
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        self.set_input(input_vector["system_input"])
        output = self.next_output

        self.next_output = self.integrate(input_vector["time"])
        try:
            self._model.check_consistency(self.next_output)
        except ModelException as e:
            raise SolverException("Timestep Integration failed! "
                                  "Model raised: {0}".format(e))
        return output

    @abstractmethod
    def set_input(self, *args):
        pass

    @abstractmethod
    def integrate(self, t):
        pass

    @property
    @abstractmethod
    def t(self):
        pass

    @property
    @abstractmethod
    def successful(self):
        pass


class ControllerException(SimulationException):
    pass


class Controller(SimulationModule):
    """
    Base class for all user defined controllers.
    Use input_order to define order of required derivatives from the trajectory 
    generator.
    Via 'input_type' you may choose one of the sources listed in 'input_sources'
    for the feedback calculation.
    """
    # selectable input sources for controller
    input_sources = ["system_state", "system_output", "Observer"]

    def __init__(self, settings):
        SimulationModule.__init__(self, settings)
        assert ("input_order" in settings)
        assert ("input_type" in settings)
        assert (settings["input_type"] in self.input_sources)

    @property
    def input_order(self):
        return self._settings["input_order"]

    def calc_output(self, input_vector):
        input_values = next((input_vector[src] for src in self.input_sources
                             if src == self._settings["input_type"]), None)
        if input_values is None:
            raise ControllerException("Selected Input not available")
        trajectory_values = input_vector.get("Trajectory", None)
        feedforward_values = input_vector.get("Feedforward", None)

        return self._control(input_vector["time"], trajectory_values,
                             feedforward_values, input_values)

    @abstractmethod
    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        """
        placeholder for control law, for more sophisticated implementations
        overload calc_output.
        :param trajectory_values: desired values from trajectory generator
        :param feedforward_values: output of feed-forward block
        :param input_values: the input values selected by the *input_type* setting
        :param **kwargs: placeholder for custom parameters
        :return: control output
        """
        pass


class Observer(SimulationModule):
    """
    Base class for all user defined observers.
    """

    def __init__(self, settings):
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        system_input = input_vector.get("system_input", None)
        if "ObserverMixer" in input_vector:
            system_output = input_vector["ObserverMixer"]
        elif "system_output" in input_vector:
            system_output = input_vector["system_output"]
        else:
            raise SimulationException("No Observer input specified")

        return self._observe(input_vector["time"], system_input, system_output)

    @abstractmethod
    def _observe(self, time, system_input, system_output):
        """
        Placeholder for observer law.
        
        Args:
            time: Current time
            system_input: Current system input
            system_output: Current system output

        Returns:
            Estimated system state
        """
        pass


class Feedforward(SimulationModule):
    """
    Base class for all user defined feedforward
    """

    def __init__(self, settings):
        self._model = settings["modules"]["Model"]
        SimulationModule.__init__(self, settings)
        assert ("input_order" in settings)

    @property
    def input_order(self):
        return self._settings["input_order"]

    def calc_output(self, input_dict):
        return self._feedforward(input_dict["time"], input_dict["Trajectory"])

    @abstractmethod
    def _feedforward(self, time, trajectory_values):
        """
        placeholder for feedforward calculation
        :param trajectory_values: values from trajectory with there derivation
        :return: feedforward output
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
        control_order = 0
        feedforward_order = 0
        if "Controller" in settings["modules"].keys():
            control_order = settings["modules"]["Controller"].input_order
        if "Feedforward" in settings["modules"].keys():
            feedforward_order = settings["modules"]["Feedforward"].input_order
        settings.update(differential_order=max([control_order, feedforward_order]))
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        desired = self._desired_values(input_vector["time"])
        return desired

    @abstractmethod
    def _desired_values(self, t):
        pass


class MixerException(Exception):
    pass


class SignalMixer(SimulationModule):
    """
    Base class for all Signal mixing modules
    """
    def __init__(self, settings):
        assert "input signals" in settings
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        signals = [value for signal, value in input_vector.items()
                   if signal in self._settings["input signals"]]
        return self._mix(signals)


class ModelMixer(SignalMixer):
    pass


class ObserverMixer(SignalMixer):
    pass


class Limiter(SimulationModule):
    """
    Base class for all limiter variants
    """

    def __init__(self, settings):
        assert "input signal" in settings
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._limit(input_dict[self._settings["input signal"]])

    def _limit(self, value):
        """
        placeholder for limiter calculation
        :param value: values to limit
        :return: limiter output
        """
        return value


class Sensor(SimulationModule):
    """
    Base class for all sensor variants
    """

    def __init__(self, settings):
        assert "input signal" in settings
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._measure(input_dict[self._settings["input signal"]])

    def _measure(self, value):
        """
        placeholder for measurement calculation
        in here you can select which state elements you want to measure or add measurement delays

        :param value: values to measure
        :return: sensor output
        """
        return value


class Disturbance(SimulationModule):
    """
    Base class for all disturbance variants
    """

    def __init__(self, settings):
        assert "input signal" in settings
        settings.update({"tick divider": 1})
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._disturb(input_dict[self._settings["input signal"]])

    @abstractmethod
    def _disturb(self, value):
        """
        placeholder for disturbance calculation
        if the noise shall be dependent on the measured signal use it to create noise

        :param value: values that was measured
        :return: noise that is to be added to the signal later on
        """
        pass
