from collections import OrderedDict
import os
import pickle

from scipy.integrate import ode
from scipy.signal import StateSpace
import sympy as sp
import numpy as np

from .simulation_modules import (
    Model, Solver, SolverException, Trajectory, TrajectoryException, Controller,
    Feedforward, SignalMixer, ModelMixer, ObserverMixer, Limiter, Sensor,
    Disturbance
)
from .controltools import calc_prefilter, place_siso

__all__ = ["LinearStateSpaceModel", "ODEInt", "ModelInputLimiter",
           "Setpoint", "HarmonicTrajectory", "SmoothTransition",
           "PIDController", "LinearStateSpaceController",
           "DeadTimeSensor", "GaussianNoise",
           "AdditiveMixer"]

"""
Ready to go implementations of simulation modules.
"""


class LinearStateSpaceModel(Model):
    """
    The state space model of a linear system.

    The parameters of this model can be provided in form of a file whose path is
    given by the setting ``config file`` .
    This path should point to a pickled dict holding the following keys:

        `system`:
            An Instance of :py:class:`scipy.signal.StateSpace` (from scipy)
            representing the system,
        `op_inputs`:
            An array-like object holding the operational point's inputs,
        `op_outputs`:
            An array-like object holding the operational point's outputs.

    """
    public_settings = OrderedDict([
        ("config file", None),
        ("initial state", None),
        ("initial output", None),
    ])

    def __init__(self, settings):
        file = settings["config file"]
        assert os.path.isfile(file)

        with open(file, "rb") as f:
            data = pickle.load(f)

        if "system" not in data:
            raise ValueError("Config file lacks mandatory settings.")

        self.ss = data["system"]

        # no feedthrough possible
        np.testing.assert_array_equal(self.ss.D, np.zeros_like(self.ss.D))

        settings["state_count"] = self.ss.B.shape[0]
        settings["input_count"] = self.ss.B.shape[1]

        self.input_offset = data.get("op_inputs",
                                     np.zeros((self.ss.B.shape[1], )))
        if len(self.input_offset) != self.ss.B.shape[1]:
            raise ValueError("Provided input offset does not match input "
                             "dimensions.")

        self.output_offset = data.get("op_outputs",
                                      np.zeros((self.ss.C.shape[0], )))
        if len(self.output_offset) != self.ss.C.shape[0]:
            raise ValueError("Length of provided output offset does not match "
                             "output dimensions ({} != {}).".format(
                len(self.output_offset),
                self.ss.C.shape[0]
            ))

        if settings["initial state"] is None:
            if settings["initial output"] is None:
                raise ValueError("Neither 'initial state' nor 'initial output'"
                                 "given.")

            settings["initial state"] = \
                np.linalg.pinv(self.ss.C) @ (settings["initial output"]
                                             - self.output_offset)

        super().__init__(settings)

    def state_function(self, t, x, args):
        return np.squeeze(self.ss.A @ x + self.ss.B @ (
            args[0] - self.input_offset))

    def calc_output(self, input_vector):
        return (self.ss.C @ input_vector
                + self.output_offset)


class ODEInt(Solver):
    """
    Wrapper for ode_int from Scipy project
    """
    public_settings = OrderedDict([
        ("Mode", "vode"),
        ("Method", "adams"),
        ("measure rate", 500),
        ("step size", 1e-3),
        ("rTol", 1e-6),
        ("aTol", 1e-9),
        ("start time", 0),
        ("end time", 5)
    ])

    def __init__(self, settings):
        Solver.__init__(self, settings)

        # setup solver
        if hasattr(self._model, "jacobian"):
            self._solver = ode(self._model.state_function,
                               jac=self._model.jacobian)
        else:
            self._solver = ode(self._model.state_function)

        self._solver.set_integrator(self._settings["Mode"],
                                    method=self._settings["Method"],
                                    rtol=self._settings["rTol"],
                                    atol=self._settings["aTol"],
                                    max_step=self._settings["step size"]
                                    )
        self._solver.set_initial_value(np.atleast_1d(self._model.initial_state),
                                       t=self._settings["start time"])

    @property
    def t(self):
        return self._solver.t

    @property
    def successful(self):
        return self._solver.successful()

    def set_input(self, *args):
        """
        propagate input changes to ode_int
        """
        self._solver.set_f_params(args)
        if hasattr(self._model, "jacobian"):
            # TODO Test
            self._solver.set_jac_params(args)

    def integrate(self, t):
        """
        Integrate until target step is reached.

        :param t: target time
        :return: system state at target time
        """
        state = self._solver.integrate(t + self._settings["step size"])

        # check model constraints
        new_state = self._model.root_function(state)
        if new_state[0]:
            # reset solver since discontinuous change in equations happened
            self._solver.set_initial_value(new_state[1], self.t)

        if not self._solver.successful():
            raise SolverException("Integration has not been successful.")

        return state


class SmoothTransition(Trajectory):
    """
    provides (differential) smooth transition between two scalar states
    """
    # TODO enable generation of transitions for state vector
    public_settings = {"states": [0, 1],
                       "start time": 0,
                       "delta t": 5,
                       }

    def __init__(self, settings):
        Trajectory.__init__(self, settings)

        # setup symbolic expressions
        tau, k = sp.symbols('tau, k')

        gamma = self._settings["differential_order"] + 1
        alpha = sp.factorial(2 * gamma + 1)

        f = sp.binomial(gamma, k) * (-1) ** k * tau ** (gamma + k + 1) / (gamma + k + 1)
        phi = alpha / sp.factorial(gamma) ** 2 * sp.summation(f, (k, 0, gamma))

        # differentiate phi(tau), index in list corresponds to order
        dphi_sym = [phi]  # init with phi(tau)
        for order in range(self._settings["differential_order"]):
            dphi_sym.append(dphi_sym[-1].diff(tau))

        # lambdify
        self.dphi_num = []
        for der in dphi_sym:
            self.dphi_num.append(sp.lambdify(tau, der, 'numpy'))

    def _desired_values(self, t):
        """
        Calculates desired trajectory
        """
        y = np.zeros((len(self.dphi_num),))
        yd = self._settings['states']
        t0 = self._settings['start time']
        dt = self._settings['delta t']

        if t < t0:
            y[0] = yd[0]
        elif t > t0 + dt:
            y[0] = yd[1]
        else:
            for order, dphi in enumerate(self.dphi_num):
                if order == 0:
                    ya = yd[0]
                else:
                    ya = 0

                y[order] = ya + (yd[1] - yd[0]) * dphi((t - t0) / dt) * 1 / dt ** order

        return y


class HarmonicTrajectory(Trajectory):
    """
    This generator provides a scalar harmonic sinus signal
    with derivatives up to order n
    """

    public_settings = OrderedDict([("Amplitude", 0.25),
                                   ("Frequency", 0.1),
                                   ("Offset", 0.75),
                                   ("Phase in degree", 0)])

    def __init__(self, settings):
        Trajectory.__init__(self, settings)

        # calculate symbolic derivatives up to order n
        t, a, f, off, p = sp.symbols("t, a, f, off, p")
        self.yd_sym = []
        harmonic = a * sp.sin(2 * sp.pi * f * t + p) + off

        for idx in range(settings["differential_order"] + 1):
            self.yd_sym.append(harmonic.diff(t, idx))

        # lambdify
        for idx, val in enumerate(self.yd_sym):
            self.yd_sym[idx] = sp.lambdify((t, a, f, off, p), val, "numpy")

    def _desired_values(self, t):
        # yd = []
        yd = np.zeros((self._settings['differential_order'] + 1), )

        a = self._settings['Amplitude']
        f = self._settings['Frequency']
        off = self._settings["Offset"]
        p = self._settings["Phase in degree"] * np.pi / 180

        for idx, val in enumerate(self.yd_sym):
            yd[idx] = val(t, a, f, off, p)
            # yd.append(val(t, a, f, off, p))

        return yd


class Setpoint(Trajectory):
    """
    provides a setpoint selection for arbitrary states
    if a state is not selected it gets the setpoint 0
    """

    public_settings = OrderedDict([("State", [2, 4]),
                                   ("Setpoint", [0, 0])])

    def __init__(self, settings):
        Trajectory.__init__(self, settings)
        if len(self._settings["State"]) != len(self._settings["Setpoint"]):
            raise TrajectoryException("Dimension mismatch between selected "
                                      "states and  the given setpoints.")

    def _desired_values(self, t):
        yd = np.zeros((len(self._settings["Setpoint"]),
                       self._settings["differential_order"] + 1))

        for idx, val in enumerate(self._settings["Setpoint"]):
            yd[idx, 0] = val

        return yd


class LinearStateSpaceController(Controller):
    """
    A controller that is based on a state space model of a linear system.

    This controller needs a linear statespace model, just as the
    :py:class:`LinearStateSpaceModel` . The file provided in ``config file``
    should therefore contain a dict holding the entries: ``model``,
    ``op_inputs`` and ``op_outputs`` .

    If poles is given (differing from `None` ) the state-feedback will be
    computed using :py:func:`pymoskito.place_siso` .
    Furthermore an appropriate prefilter is calculated, which establishes
    stationary attainment of the desired output values.

    Note:
        If a SIMO or MIMO system is given, the control_ package as well as the
        slycot_ package are needed the perform the pole placement.


    .. _control: https://github.com/python-control/python-control
    .. _slycot: https://github.com/python-control/Slycot
    """

    public_settings = OrderedDict([
        ("input source", "system_state"),
        ("config file", None),
        ("poles", None),
    ])

    def __init__(self, settings):
        file = settings["config file"]
        assert os.path.isfile(file)

        with open(file, "rb") as f:
            data = pickle.load(f)

        if "system" not in data:
            raise ValueError("Config file lacks mandatory settings.")

        self.ss = data["system"]

        self.input_offset = data.get("op_inputs", None)
        self.output_offset = data.get("op_outputs", None)

        if self.input_offset is None:
            self.input_offset = np.zeros((self.ss.B.shape[1], ))
        if len(self.input_offset) != self.ss.B.shape[1]:
            raise ValueError("Provided input offset does not match input "
                             "dimensions.")

        if self.output_offset is None:
            self.output_offset = np.zeros((self.ss.C.shape[0], ))
        if len(self.output_offset) != self.ss.C.shape[0]:
            raise ValueError("Length of provided output offset does not match "
                             "output dimensions ({} != {}).".format(
                len(self.output_offset),
                self.ss.C.shape[0]
            ))

        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=self.ss.C.shape[0])
        settings.update(input_type=settings["input source"])
        super().__init__(settings)

        if settings.get("poles", None) is None:
            # pretty useless but hey why not.
            self.feedback = np.zeros((self.ss.B.shape[1], self.ss.A.shape[0]))
        else:
            if self.ss.B.shape[1] == 1:
                # save the control/slycot dependency
                self.feedback = place_siso(self.ss.A,
                                           self.ss.B,
                                           self.settings["poles"])
            else:
                import control
                self.feedback = control.place(self.ss.A,
                                              self.ss.B,
                                              self.settings["poles"])

        self.prefilter = calc_prefilter(self.ss.A, self.ss.B, self.ss.C,
                                        self.feedback)

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        return (-self.feedback @ input_values
                + self.prefilter @ (trajectory_values[:, 0] -
                                    self.output_offset)
                + self.input_offset)


class PIDController(Controller):
    """
    PID Controller
    """
    public_settings = OrderedDict([("Kp", 700),
                                   ("Ki", 500),
                                   ("Kd", 200),
                                   ("output_limits", [0, 255]),
                                   ("input_state", [2]),
                                   ("tick divider", 1)])
    last_time = 0

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=len(self.public_settings["input_state"]))
        settings.update(input_type="system_state")
        Controller.__init__(self, settings)

        # define variables for data saving in the right dimension
        self.e_old = np.zeros((len(self._settings["input_state"]), ))  # column vector
        self.integral_old = np.zeros((len(self._settings["input_state"]), ))  # column vector
        self.last_u = np.zeros((len(self._settings["input_state"]), ))  # column vector
        self.output = np.zeros((len(self._settings["input_state"]), ))  # column vector

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        # input abbreviations
        x = np.zeros((len(self._settings["input_state"]), ))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx] = input_values[int(state)]

        yd = trajectory_values

        # step size
        dt = time - self.last_time
        # save current time
        self.last_time = time

        if dt != 0:
            for i in range(len(x)):
                # error
                e = yd[i] - x[i]
                integral = e * dt + self.integral_old[i]
                if integral > self._settings["output_limits"][1]:
                    integral = self._settings["output_limits"][1]
                elif integral < self._settings["output_limits"][0]:
                    integral = self._settings["output_limits"][0]
                differential = (e - self.e_old[i]) / dt

                self.output[i] = (self._settings["Kp"] * e
                                  + self._settings["Ki"] * integral
                                  + self._settings["Kd"] * differential)

                if self.output[i] > self._settings["output_limits"][1]:
                    self.output[i] = self._settings["output_limits"][1]
                elif self.output[i] < self._settings["output_limits"][0]:
                    self.output[i] = self._settings["output_limits"][0]

                # save data for new calculation
                self.e_old[i] = e
                self.integral_old[i] = integral
            u = self.output
        else:
            u = self.last_u
        self.last_u = u
        return u


class AdditiveMixer(SignalMixer):
    """
    Signal Mixer that accumulates all input signals.

    Processing is done according to rules of numpy broadcasting.
    """
    public_settings = OrderedDict([("Input A", None),
                                   ("Input B", None)])

    def __init__(self, settings):
        settings.update([("input signals", [settings["Input A"],
                                            settings["Input B"]])])
        SignalMixer.__init__(self, settings)

    def _mix(self, signal_values):
        return sum(signal_values)


class ModelInputLimiter(Limiter):
    """
    ModelInputLimiter that limits the model input values.

    Settings:
        `Limits`: (List of) list(s) that hold (min, max) pairs for the
        corresponding input.
    """

    public_settings = OrderedDict([("Limits", [None, None])])

    def __init__(self, settings):
        settings.update([("input_signal", "ModelMixer")])
        Limiter.__init__(self, settings)
        self.limits = np.atleast_2d(settings["Limits"])

    def _limit(self, values):
        val = np.atleast_1d(values)
        out = np.zeros_like(val)
        for idx, v in enumerate(val):
            lim = self.limits[idx]
            if lim[0] is None and lim[1] is None:
                out[idx] = v
            else:
                out[idx] = np.clip(v, *lim)

        if len(values.shape) == 1:
            return out.flatten()
        else:
            return out


class DeadTimeSensor(Sensor):
    """
    Sensor that adds a measurement delay on chosen states
    """

    public_settings = OrderedDict([("states to delay", [0]),
                                   ("delay", 1)])

    def __init__(self, settings):
        settings.update([("input signal", "system_state")])
        Sensor.__init__(self, settings)
        self._storage = None

    def _measure(self, value):
        if self._storage is None:
            # create storage with length "delay"
            # initial values are the first input
            self._storage = [value]*int(self._settings["delay"])

        # save current values
        measurement = value.copy()
        # add new measurement
        self._storage.append(value)

        # get delayed measurements
        delayed_measurement = self._storage.pop(0)

        # replace current values with delayed values, if it is chosen
        for i in self._settings["states to delay"]:
            measurement[i] = delayed_measurement[i]

        return measurement


class GaussianNoise(Disturbance):
    """
    Noise generator for gaussian noise
    """

    public_settings = OrderedDict([("sigma", 1),
                                   ("mean", 0)])

    def __init__(self, settings):
        settings.update([("input signal", "Sensor")])
        Disturbance.__init__(self, settings)

    def _disturb(self, value):
        return np.random.normal(self._settings['mean'],
                                self._settings['sigma'],
                                value.output_dim)
