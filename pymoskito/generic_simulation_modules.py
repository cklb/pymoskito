from collections import OrderedDict
from scipy.integrate import ode
import sympy as sp
import numpy as np

# from pytrajectory import ControlSystem

from .simulation_modules import Solver, \
    SolverException, \
    Trajectory, \
    TrajectoryException, \
    Controller, \
    Feedforward, \
    SignalMixer, \
    ModelMixer, \
    ObserverMixer, \
    Limiter, \
    Sensor, \
    Disturbance

"""
ready to go implementations of simulation modules
"""


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
        integrates until target step reached
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
            raise SolverException("integration step was not successful.")

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
        y = np.zeros((1, len(self.dphi_num)))
        yd = self._settings['states']
        t0 = self._settings['start time']
        dt = self._settings['delta t']

        if t < t0:
            y[0][0] = yd[0]
        elif t > t0 + dt:
            y[0][0] = yd[1]
        else:
            for order, dphi in enumerate(self.dphi_num):
                if order == 0:
                    ya = yd[0]
                else:
                    ya = 0

                y[0][order] = ya + (yd[1] - yd[0]) * dphi((t - t0) / dt) * 1 / dt ** order

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
        yd = np.zeros((1, self._settings['differential_order'] + 1))

        a = self._settings['Amplitude']
        f = self._settings['Frequency']
        off = self._settings["Offset"]
        p = self._settings["Phase in degree"] * np.pi / 180

        for idx, val in enumerate(self.yd_sym):
            yd[0][idx] = val(t, a, f, off, p)
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
            raise TrajectoryException("The amount of states and setpoints is not equal")

    def _desired_values(self, t):
        yd = np.zeros((len(self._settings["Setpoint"]), self._settings["differential_order"] + 1))

        for idx, val in enumerate(self._settings["Setpoint"]):
            yd[idx, 0] = val

        return yd


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
        self.e_old = np.zeros((len(self._settings["input_state"]), 1))  # column vector
        self.integral_old = np.zeros((len(self._settings["input_state"]), 1))  # column vector
        self.last_u = np.zeros((len(self._settings["input_state"]), 1))  # column vector
        self.output = np.zeros((len(self._settings["input_state"]), 1))  # column vector

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        # input abbreviations
        x = np.zeros((len(self._settings["input_state"]), 1))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx][0] = input_values[int(state)][0]

        yd = trajectory_values

        # step size
        dt = time - self.last_time
        # save current time
        self.last_time = time

        if dt != 0:
            for i in range(len(x)):
                # error
                e = yd[i][0] - x[i][0]
                integral = e * dt + self.integral_old[i][0]
                if integral > self._settings["output_limits"][1]:
                    integral = self._settings["output_limits"][1]
                elif integral < self._settings["output_limits"][0]:
                    integral = self._settings["output_limits"][0]
                differential = (e - self.e_old[i][0]) / dt

                self.output[i][0] = self._settings["Kp"] * e \
                                    + self._settings["Ki"] * integral \
                                    + self._settings["Kd"] * differential

                if self.output[i][0] > self._settings["output_limits"][1]:
                    self.output[i][0] = self._settings["output_limits"][1]
                elif self.output[i][0] < self._settings["output_limits"][0]:
                    self.output[i][0] = self._settings["output_limits"][0]

                # save data for new calculation
                self.e_old[i][0] = e
                self.integral_old[i][0] = integral
            u = self.output
        else:
            u = self.last_u
        self.last_u = u
        return u


class PyTrajectory(Feedforward):
    """
    this class is WIP!
    integration  of the PyTrajectory package,
    PyTrajectory is a Python library for the determination of the feed forward control
    to achieve a transition between desired states of a nonlinear control system.
    """

    public_settings = OrderedDict([
        ("state a", [0]),
        ("state b", [0]),
        ("input a", [0]),
        ("input b", [0]),
        ("time a", 0),
        ("time b", 2),
        ("tick divider", 1)
    ])

    def __init__(self, settings):
        settings.update(input_order=0)
        Feedforward.__init__(self, settings)

        # check consistency between public_settings and the given model
        # TODO don't do this!
        assert (self._model._settings["state_count"] == len(self._settings["state a"]))
        assert (self._model._settings["state_count"] == len(self._settings["state b"]))
        assert (self._model._settings["input_count"] == len(self._settings["input a"]))
        assert (self._model._settings["input_count"] == len(self._settings["input b"]))

        # TODO get integration of PyTrajectory going
        # # calculate the feedforward
        # system = ControlSystem(self._model.f,
        #                        a=self._settings["time a"],
        #                        b=self._settings["time b"],
        #                        xa=self._settings["state a"],
        #                        xb=self._settings["state b"],
        #                        ua=self._settings["input a"],
        #                        ub=self._settings["input b"])
        # # alter some method parameters to increase performance
        # system.set_param('su', 10)
        # system.set_param('eps', 8e-2)
        # system.solve()
        #
        # self.feed_time = system.sim_data[0]
        # self.feed_u =system.sim_data[2]

    def _feedforward(self, traj_values, t):
        # TODO get rid of this extra parameter
        u_feed = 0
        return u_feed


class AdditiveMixer(SignalMixer):
    """
    Signal Mixer that ads up input signals
    processing is done according to rules of numpy casting
    """
    public_settings = OrderedDict([("Input A", None),
                                   ("Input B", None)])

    def __init__(self, settings):
        settings.update([("input signals", [settings["Input A"], settings["Input B"]])])
        SignalMixer.__init__(self, settings)

    def _mix(self, signal_values):
        return np.array([[np.sum(signal_values)]], dtype=float)


class ModelInputLimiter(Limiter):
    """
    ModelInputLimiter that limits the model input value
    """

    public_settings = OrderedDict([("Limits", [0, 240])])

    def __init__(self, settings):
        settings.update([("input signal", "ModelMixer")])
        Limiter.__init__(self, settings)

    def _limit(self, value):
        if value < self._settings["Limits"][0]:
            value = np.array([[self._settings["Limits"][0]]])  # convert number into numpy (1,1) array
        if value > self._settings["Limits"][1]:
            value = np.array([[self._settings["Limits"][1]]])  # convert number into numpy (1,1) array

        # TODO restructure to something like this:
        # value = np.max(value, self._settings["Limits"][0])
        # value = np.min(value, self._settings["Limits"][1])

        return value


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
