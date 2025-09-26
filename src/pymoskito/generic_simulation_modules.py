from collections import OrderedDict
import os
import pickle
import warnings

from scipy.integrate import ode
from scipy.interpolate import interp1d
from scipy.optimize import bisect
import sympy as sp
import numpy as np

from .simulation_modules import (
    Model, Solver, SolverException,
    Trajectory, TrajectoryException, Controller,
    Feedforward, SignalMixer, ModelMixer, ObserverMixer, Limiter, Sensor,
    Disturbance
)
from .controltools import calc_prefilter, place_siso

__all__ = ["LinearStateSpaceModel", "ODEInt", "ModelInputLimiter",
           "Setpoint", "HarmonicTrajectory", "SmoothTransition", "InterpolatorTrajectory",
           "Feedthrough",
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
    Wrapper for ode_int from the Scipy project

    Args:
        settings (OrderedDict): Dictionary holding the config options for this module.
            See :py:class:`Solver` and scipy's odeint for details.

    """
    public_settings = OrderedDict([
        ("measure rate", 500),
        ("start time", 0),
        ("end time", 5),
        ("Mode", "vode"),
        ("Method", "adams"),
        ("step size", 1e-3),
        ("rTol", 1e-6),
        ("aTol", 1e-9),
    ])

    def __init__(self, settings):
        Solver.__init__(self, settings)

        # setup bisection fields
        self._cur_state = np.atleast_1d(self._model.initial_state)
        self._cur_events = self._eval_events(self._settings["start time"], self._cur_state)

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
        self._solver.set_initial_value(self._cur_state, t=self._settings["start time"])

    def _eval_events(self, t, x):
        """ Evaluation helper for the event function """
        # call all events
        r = np.array([f(t, x) for f in self._model.events],
                     dtype=float)
        # an actual zero is counted as positive
        r[r == 0] = np.finfo(float).eps
        return r

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

    def integrate(self, *, t=None):
        """
        Solve the system equations for one step

        Args:
            t (float): Target time to stop at, if None use step size from settings
        Returns:
            system state at target time
        """
        cur_time = self.t
        cur_state = self._cur_state

        if t is None:
            new_time = cur_time + self._settings["step size"]
        else:
            new_time = t
        new_state = self._solver.integrate(new_time)
        if not self._solver.successful():
            raise SolverException("Integration failed.\n"
                                  "This can happen due to several reasons, here are some pointers:\n"
                                  "- First of all: Check the log for solver warnings\n"
                                  "- Model: Check for errors and inconsistencies in the model equations\n"
                                  "- For switching model equations: Try to provide event functions to help the solver\n"
                                  "- Controller/Feedforward: Check for unreasonably large inputs\n"
                                  "- Solver: Loosen the precision requirements by increasing aTol and/or rTol"
                                  )

        # evaluate custom event functions for new state
        new_events = self._eval_events(new_time, new_state)
        # check if any events (sign changes) occurred
        e_idxs = np.where(self._cur_events * new_events < 0)[0]

        # run bisection to get exact time for each event
        e_times = []
        for e_idx in e_idxs:
            self._logger.debug(f"Event with index {e_idx} detected between "
                               f"{cur_time} and {self.t} seconds")
            try:
                e_t = bisect(self._b_func, a=cur_time, b=self.t,
                                args=(cur_time, cur_state, e_idx))
            except SolverException as err:
                e_t = self.t
            except ValueError as err:
                    if err.args[0] == 'f(a) and f(b) must have different signs':
                        self._logger.debug("Event could not be reproduced, ignoring")
                        continue
                    else:
                        raise SolverException(f"Bisection failed with error: '{err}'")
            self._logger.debug(f"Bisection yielded event time {e_t}")
            e_times.append(e_t)

        if len(e_times) > 0:
            # take the smallest time stamp and continue
            e_idx = np.argmin(e_times)
            e_time = e_times[e_idx]

            self._logger.debug(f"Restarting at original t={cur_time} from state {cur_state} "
                               f"and solving up to event at t={e_time}")
            # reset the solver to the original starting time
            self._solver.set_initial_value(cur_state, cur_time)
            # integrate up to event time
            temp_state = self._solver.integrate(e_time)
            temp_events = self._eval_events(e_time, temp_state)
            # make sure we are on the right side of the change
            temp_events[e_idx] = np.copysign(temp_events[e_idx], new_events[e_idx])

            self._logger.debug(f"Restarting at event t={e_time} from state {temp_state} "
                               f"and solving up to desired t={new_time}")
            # reset the solver to the event time
            self._solver.set_initial_value(temp_state, e_time)
            # integrate up to the desired time
            self._cur_state = temp_state
            self._cur_events = temp_events
            new_state = self.integrate(t=new_time)
            self._logger.debug(f"Event handled")

        # update internal fields
        self._cur_state = new_state
        self._cur_events = new_events

        return new_state

    def _b_func(self, t_end, t_start, x_start, e_idx):
        """
        Helper function for bisection of the exact event time
        """
        self._solver.set_initial_value(x_start, t_start)
        x_end = self._solver.integrate(t_end)
        if not self._solver.successful():
            raise SolverException("Solver failed during bisection")
        e_end = self._eval_events(t_end, x_end)
        return e_end[e_idx]


class SmoothTransition(Trajectory):
    """
    provides (differential) smooth transition between two scalar states
    """
    public_settings = {"states": [[0, 1]],
                       "start time": 0,
                       "delta t": 5,
                       }

    def __init__(self, settings):
        settings["states"] = np.asarray(settings["states"])
        Trajectory.__init__(self, settings)

        # setup symbolic expressions
        tau, k = sp.symbols("tau, k")

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
            self.dphi_num.append(sp.lambdify(tau, der, "numpy"))

        # issue deprecation warning
        if self._settings["states"].ndim == 1:
            msg = "SmoothTransition will require 2d data for 'states' " \
                  "in the next version, please update your configuration."
            warnings.warn(msg, DeprecationWarning)
            self._logger.warn(msg)
            self._settings["states"] = self._settings["states"][None, :]

    def _desired_values(self, t):
        """
        Calculates desired trajectory
        """
        yd = self._settings['states']
        t0 = self._settings['start time']
        dt = self._settings['delta t']

        y = np.zeros((yd.shape[0], len(self.dphi_num)))
        if t < t0:
            y[:, 0] = yd[:, 0]
        elif t > t0 + dt:
            y[:, 0] = yd[:, 1]
        else:
            for order, dphi in enumerate(self.dphi_num):
                if order == 0:
                    ya = yd[:, 0]
                else:
                    ya = np.zeros_like(yd[:, 0])

                scale = dphi((t - t0) / dt) * 1 / dt ** order
                y[:, order] = ya + (yd[:, 1] - yd[:, 0]) * scale

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
    Provides setpoints for every output component.

    If the output is not scalar, just add more entries to the list.
    By querying the differential order from the controller (if available) the
    required derivatives are given.

    Note:
        Keep in mind that while this class provides zeros for all derivatives
        of the desired value, they actually strive to infinity for :math:`t=0` .
    """

    public_settings = OrderedDict([("Setpoint", [0])])

    def __init__(self, settings):
        Trajectory.__init__(self, settings)
        self.yd = np.zeros((len(self._settings["Setpoint"]),
                            self._settings["differential_order"] + 1))

        for idx, val in enumerate(self._settings["Setpoint"]):
            self.yd[idx, 0] = val

    def _desired_values(self, t):
        return self.yd


class InterpolatorTrajectory(Trajectory):
    """
    Generic trajectory that interpolates between the given values

    This class basically is a wrapper for scipy's `interp1d`.

    Note:
        Values outside the given time domain will not be extrapolated but held
        at their last values.

    Parameters:
        kind (string): The type of interpolation to use, possible values are
        'linear', 'nearest', 'nearest-up', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', or 'next'.
        x_data (array): Time steps to work on
        y_data (array): Corresponding values
    """
    public_settings = OrderedDict([
        ("kind", "zero"),
        ("x_data", [0, 1]),
        ("y_data", [0, 10]),
    ])

    def __init__(self, settings):
        super().__init__(settings)
        x_data = settings["x_data"]
        y_data = settings["y_data"]
        self._interp = interp1d(x=x_data,
                                y=y_data,
                                kind=settings["kind"],
                                bounds_error=False,
                                fill_value=(y_data[0], y_data[-1]),
                                )

    def _desired_values(self, t):
        return self._interp(t)


class Feedthrough(Feedforward):
    """
    A simple feedthrough that passes the reference trajectory to its output.
    """
    public_settings = OrderedDict([
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        settings.update(input_order=0)
        Feedforward.__init__(self, settings)

    def _feedforward(self, time, trajectory_values):
        return trajectory_values


class LinearStateSpaceController(Controller):
    """
    A controller that is based on a state space model of a linear system.

    This controller needs a linear statespace model, just as the
    :py:class:`LinearStateSpaceModel` . The file provided in ``config file``
    should therefore contain a dict holding the entries: ``model``,
    ``op_inputs`` and ``op_outputs`` .

    If poles is given (differing from `None` ) the state-feedback will be
    computed using :py:func:`pymoskito.place_siso` .
    Furthermore, an appropriate prefilter is calculated, which establishes
    stationary attainment of the desired output values.

    Note:
        If a SIMO or MIMO system is given, the control_ package as well as the
        slycot_ package are needed the perform the pole placement.


    .. _control: https://github.com/python-control/python-control
    .. _slycot: https://github.com/python-control/Slycot
    """

    public_settings = OrderedDict([
        ("input source", "Model_State"),
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
    A simple scalar PID Controller with basic anti-windup

    This class will run a PID controller with the given settings for each
    component of the model output listed in 'input indexes'.
    """
    public_settings = OrderedDict([
        ("input indexes", [0]),
        ("Kp", 1),
        ("Ki", 1),
        ("Kd", 1),
        ("output limits", [-1, 1]),
        ("tick divider", 1)])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)  # no reference derivatives required
        settings.update(input_type="Model_Output")  # use the model output to compute the control error
        output_dim = len(self.public_settings["input indexes"])
        settings.update(output_dim=output_dim)
        Controller.__init__(self, settings)

        self.dt = settings["step size"]
        self.error_integral = np.zeros(output_dim)
        self.previous_error = np.zeros(output_dim)

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        #  compute the control error
        y = np.asarray(input_values)[self._settings["input indexes"]]
        yd = np.atleast_2d(trajectory_values)[:, 0]  # ignore reference derivatives
        error = yd - y

        # compute the error integral
        integral = self.error_integral + error * self.dt

        # compute the error derivative
        differential = (error - self.previous_error) / self.dt

        # compute control outputs
        output = (self._settings["Kp"] * error
                          + self._settings["Ki"] * integral
                          + self._settings["Kd"] * differential)

        # saturate the outputs
        sat_output = np.clip(output, *self._settings["output limits"])

        # only integrate errors of unsaturated outputs
        unsat_idxs = output == sat_output
        self.error_integral[unsat_idxs] = integral[unsat_idxs]

        # store current error
        self.previous_error = error

        return sat_output


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
        settings.update([("input signal", "Model_State")])
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
        settings.update([("input signal", "Model_Output")])
        Disturbance.__init__(self, settings)

    def _disturb(self, t, signal):
        return np.random.normal(self._settings['mean'],
                                self._settings['sigma'],
                                signal.shape)
