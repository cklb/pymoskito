"""
Base classes for all modules of the simulation loop.

Every block of the pymoskito simulation loop is implemented
by subclassing `SimulationModule`.
"""
import logging
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from copy import copy

from PyQt5.QtCore import QObject

pyqtWrapperType = type(QObject)

__all__ = ["SimulationModule", "SimulationException",
           "Trajectory", "Feedforward", "Controller", "Limiter",
           "ModelMixer", "Model", "ModelException",
           "Solver", "Disturbance", "Sensor", "ObserverMixer", "Observer"]


class SimulationModuleMeta(ABCMeta, pyqtWrapperType):
    pass


class SimulationException(Exception):
    pass


class SimulationModule(QObject, metaclass=SimulationModuleMeta):
    """
    Base unit of the simulation framework.

    This class provides necessary functions like output calculation and holds
    all settings that can be accessed by the user.
    The :py:attr:`public_settings` are read by the
    :py:class:`.SimulationInterface` and the rendered by the GUI. All entries
    stated in this dictionary will be available as editable settings for the
    module.
    On initialization, a possibly modified (in terms of its values) version of
    this dict will be passed back to this class and is thenceforward available
    via the :py:attr:`settings` property.

    The most important method is :py:func:`calc_output` which is called by the
    :py:class:`Simulator` to retrieve this modules output.

    Args:
        settings(OrderedDict): Settings for this simulation module.
            These entries will be shown in the properties view and can be
            changed by the user. The important entries for this base class are:

            `tick_divider`:
                See the property.
            `output info`:
                Dict holding information about the model output that are used
                in the GUI. For every item in the output array, a key for its
                index can be provided, under whose value another dict with the
                keys keys `Name` and `Unit` is expected.
                If available, these information are used to display reasonable
                names in the result view and to display the corresponding units
                for the result plots.

    Warn:
        Do NOT use '.' in the `output_info` name field.

    TODO:
        Get rid of the point restriction
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
        """
        Dict of public settings.

        This contains all settings that will be shown and can be edited
        in the GUI.
        """
        pass

    @property
    def settings(self):
        return self._settings

    @property
    def tick_divider(self):
        """
        Simulation tick divider.

        This property controls the frequency at which this Module is evaluated
        in the main simulation loop. If e.g. a value of `2` is provided, the
        module will be evaluated at every 2nd step that the solver makes.

        This feature comes in handy if discrete setups with different sample rates
        are simulated.

        Note:
            This setting is ignored for the Solver module, whose `tick_divider` is
            fixed at 1.
        """
        return self._settings["tick divider"]

    @property
    def step_width(self):
        """
        The discrete step width that this module is called with.

        This parameter will be set when the simulation is initialised
        and is based on the solver step size and the selected tick
        divider of the module.
        """
        return self._settings["step width"]

    @step_width.setter
    def step_width(self, value):
        self._settings["step width"] = value

    @abstractmethod
    def calc_output(self, input_vector):
        """
        Main evaluation routine.

        Every time the solver has made the amount of steps specified in `tick_divider`,
        this method will be called to compute the next output of the module.
        This is typically where the main logic of a module is implemented.
        """
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
        settings (OrderedDict): Dictionary holding the config options for this module.
            It *must* contain the following keys:

            :input_count:
                The length of the input vector for this model.

            :state_count:
                The length of the state vector for this model.

            :initial state:
                The initial state vector for this model.
    """

    def __init__(self, settings):
        SimulationModule.__init__(self, settings)
        assert ("state_count" in settings)
        assert ("input_count" in settings)
        assert ("initial state" in settings)
        assert len(settings["initial state"]) == settings["state_count"]

    @property
    def initial_state(self):
        """ Return the initial state of the model. """
        return self._settings["initial state"]

    @abstractmethod
    def state_function(self, t, x, args):
        """
        Calculate the state derivatives of a system with state x at time t.

        Args:
            x(Array-like): System state.
            t(float): System time.
            args: Extra arguments.

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
    """
    Exception to be raised if the solver encounters any problems
    while integrating the system.
    """
    pass


class Solver(SimulationModule):
    """
    Base Class for solver implementations.

    After initialization, for every step in the simulation
    `set_input` will be called, followed by `integrate`.
    """

    def __init__(self, settings):
        assert isinstance(settings["modules"]["Model"], Model)
        self._model = settings["modules"]["Model"]
        self.next_output = None
        SimulationModule.__init__(self, settings)
        assert self.tick_divider == 1

    def calc_output(self, input_vector):
        self.set_input(input_vector["model_input"])
        output = self.next_output

        self.next_output = self.integrate(input_vector["time"])
        try:
            self._model.check_consistency(self.next_output)
        except ModelException as e:
            raise SolverException("Time step integration failed! "
                                  "Model raised: {0}".format(e))
        return output

    @abstractmethod
    def set_input(self, *args):
        """
        Updates the inputs for the next integration step.
        """
        pass

    @abstractmethod
    def integrate(self, t):
        """
        Perform numerical integration.

        Args:
            t(float): New time up to which the model is to be integrated.
        """
        pass

    @property
    @abstractmethod
    def t(self):
        """
        The current simulation time.
        """
        pass

    @property
    @abstractmethod
    def successful(self):
        pass


class ControllerException(SimulationException):
    """
    Exception to be raised if the controller encounters any problems.
    """
    pass


class Controller(SimulationModule):
    """
    Base class for controllers.

    After subclassing, the method `_control` has to be implemented.

    Args:
        settings (OrderedDict): Dictionary holding the config options for this module.
            It must contain the following keys:

            :input_order:
                The order of required derivatives from the trajectory generator.

            :input_type:
                Source for the feedback calculation and one of the following:
                `Model_State` , `Model_Output` , `Observer` or `Sensor` .
    """
    # selectable input sources for controller
    input_sources = ["Model_State", "Model_Output", "Observer", "Sensor"]

    def __init__(self, settings):
        assert ("input_order" in settings)
        assert ("input_type" in settings)
        SimulationModule.__init__(self, settings)
        if self._settings["input_type"] == "system_state":
            self._logger.warning(
                "Input source `system_state` is being deprecated in favour of `Model_State`."
                " Please adapt your implementation.")
            self._settings["input_type"] = "Model_State"
        if self._settings["input_type"] == "system_output":
            self._logger.warning(
                "Input source `system_output` is being deprecated in favour of `Model_Output`."
                " Please adapt your implementation.")
            self._settings["input_type"] = "Model_Output"
        assert (self._settings["input_type"] in self.input_sources)

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
        Placeholder for control law calculations.

        For more sophisticated implementations overload :py:func:`calc_output` .

        Args:
            time (float): Current time.
            trajectory_values (array-like): Desired values from the trajectory
                generator.
            feedforward_values (array-like): Output of feedforward block.
            input_values (array-like): The input values selected by
                ``input_type`` .
            **kwargs: Placeholder for custom parameters.

        Returns:
            Array: Control output.
        """
        pass


class Observer(SimulationModule):
    """
    Base class for observers.

    After subclassing, the method `_observe` has to be implemented.
    """

    def __init__(self, settings):
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        model_input = input_vector.get("model_input", None)
        if "ObserverMixer" in input_vector:
            model_output = input_vector["ObserverMixer"]
        elif "Model_Output" in input_vector:
            model_output = input_vector["Model_Output"]
        else:
            raise SimulationException("No Observer input specified")

        return self._observe(input_vector["time"], model_input, model_output)

    @abstractmethod
    def _observe(self, time, system_input, system_output):
        """
        Placeholder for observer law.

        Note:
            For integration of the observer dynamics, the attribute `step_width`
            should be used the use the correct step size.
        
        Args:
            time: Current time.
            system_input: Current system input.
            system_output: Current system output.

        Returns:
            Estimated system state
        """
        pass


class Feedforward(SimulationModule):
    """
    Base class for all feedforward implementations.

    After subclassing, the method `_feedforward` has to be implemented.
    """

    def __init__(self, settings):
        self._model = settings["modules"]["Model"]
        SimulationModule.__init__(self, settings)
        assert ("input_order" in settings)

    @property
    def input_order(self):
        """
        This field can be used to specify
        the derivative order of the reference trajectories that have to
        be provided by the trajectory generator.
        """
        return self._settings["input_order"]

    def calc_output(self, input_dict):
        return self._feedforward(input_dict["time"], input_dict["Trajectory"])

    @abstractmethod
    def _feedforward(self, time, trajectory_values):
        """
        Placeholder for feedforward calculations.

        Args:
            time (float): Current time.
            trajectory_values(array-like): Desired values from the trajectory
                generator.

        Returns:
            Array: Feedforward output. This signal can be added to the
            controllers output via the :py:class:`.ModelMixer` and is also
            directly passed to the controller.
        """
        pass


class TrajectoryException(SimulationException):
    """
    Exception to be raised for errors during trajectory generation.
    """
    pass


class Trajectory(SimulationModule):
    """
    Base class for all trajectory generators.
    """

    def __init__(self, settings):
        if "modules" in settings:
            control_order = 0
            feedforward_order = 0
            if "Controller" in settings["modules"].keys():
                control_order = settings["modules"]["Controller"].input_order
            if "Feedforward" in settings["modules"].keys():
                feedforward_order = settings["modules"]["Feedforward"
                ].input_order
            settings.update(differential_order=max([control_order,
                                                    feedforward_order]))
        else:
            assert "differential_order" in settings
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        desired = self._desired_values(input_vector["time"])
        return desired

    @abstractmethod
    def _desired_values(self, t):
        """
        Placeholder for calculations of desired values.

        Args:
            t (float): Time.

        Returns:
            Array: Trajectory output. This should always be a two-dimensional
            array holding the components in to 0th and their derivatives in
            the 1th axis.
        """
        pass


class MixerException(Exception):
    pass


class SignalMixer(SimulationModule):
    """
    Base class for all Signal mixing modules
    """

    def __init__(self, settings):
        assert "input signals" in settings
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_vector):
        signals = [input_vector[s]
                   for s in self._settings["input signals"]
                   if s != "None" and s is not None]
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
        assert "input_signal" in settings
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._limit(input_dict[self._settings["input_signal"]])

    def _limit(self, values):
        """
        Placeholder for actual limit calculations.

        Args:
            values(array-like): Values to limit.

        Returns:
            Array: Limited output.
        """
        return values


class Sensor(SimulationModule):
    """
    Base class for all sensor variants
    """

    def __init__(self, settings):
        assert "input signal" in settings
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._measure(input_dict[self._settings["input signal"]])

    def _measure(self, value):
        """
        Placeholder for measurement calculations.

        One may reorder or remove state elements or introduce measurement delays
        here.

        Args:
            value (array-like float): Values from the source selected by the
                ``input_signal`` property.
        Returns:
            array-like float: 'Measured' values.
        """
        return value


class Disturbance(SimulationModule):
    """
    Base class for all disturbance variants
    """

    def __init__(self, settings):
        assert "input signal" in settings
        SimulationModule.__init__(self, settings)

    def calc_output(self, input_dict):
        return self._disturb(
            input_dict["time"],
            input_dict.get(self._settings["input signal"], None))

    @abstractmethod
    def _disturb(self, t, signal):
        """
        Placeholder for disturbance calculations.

        If the noise is to be dependent on the measured signal use its `value`
        to create the noise.

        Args:
            t (float): Current simulation time.
            signal (array-like float): Values from the source selected by the
                ``input_signal`` property.
        Returns:
            array-like float: Noise that will be mixed with a signal later on.
        """
        pass
