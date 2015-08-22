__author__ = 'stefan'
"""
ready to go implementations of generic simulation modules
"""

from collections import OrderedDict

from scipy.integrate import ode
import sympy as sp
import numpy as np

import pymoskito as pm
from simulation_modules import Solver, SolverException, Trajectory, Controller, SignalMixer, ModelMixer, ObserverMixer


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
            self._solver = ode(self._settings["Model"].state_function)

        self._solver.set_integrator(self._settings["Mode"],
                                    method=self._settings["Method"],
                                    rtol=self._settings["rTol"],
                                    atol=self._settings["aTol"],
                                    max_step=self._settings["step size"]
                                    )
        self._solver.set_initial_value(self._model.initial_state,
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
            raise SolverException("integration step was not succesful.")

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
        y = [0]*len(self.dphi_num)
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

                y[order] = ya + (yd[1] - yd[0])*dphi((t - t0)/dt)*1/dt**order

        return y

# sorry for this class, but i needed a Trajectory with a specific degree
class PolynomialTrajectory(Trajectory):
    """
    provides a smooth trajectory with a chosen degree
    """

    public_settings = {
        'degree': 9,
        'x0': 0.2,
        'xe': 1.0,
        't0': 5,
        'te': 10,
    }

    def __init__(self, settings):
        Trajectory.__init__(self, settings)

         # calculate gamma
        if self.public_settings['degree'] % 2 == 0:
            raise ValueError('Degree must be odd')

        gamma = int((self.public_settings['degree'] - 1)/2)

        # calculate alpha
        alpha = sp.factorial(2*gamma + 1)

        # calculate symbolic expressions
        tau, k = sp.symbols('tau, k')

        f = sp.binomial(gamma, k) * (-1)**k * tau**(gamma+k+1) / (gamma+k+1)
        phi = alpha/sp.factorial(gamma)**2 * sp.summation(f, (k, 0, gamma))

        # diff
        dphi_sym = [phi]
        for order in range(self._settings["differential_order"]):
            dphi_sym.append(dphi_sym[-1].diff(tau))

        self.dphi_num = []
        for derivation in dphi_sym:
            self.dphi_num.append(sp.lambdify(tau, derivation, 'numpy'))

    def _desired_values(self, t):
        """
        Calculates desired trajectory
        """

        yd = [0]*len(self.dphi_num)
        t0 = self._settings['t0']        # start time
        te = self._settings['te']        # end time

        if t < t0:
            yd[0] = self._settings['x0']
        elif t > te:
            yd[0] = self._settings['xe']
        else:
            for order, dphi in enumerate(self.dphi_num):

                if not order:
                    x0 = self._settings['x0']
                else:
                    x0 = 0

                yd[order] = x0 + (self._settings['xe'] - self._settings['x0'])\
                                 * dphi((t - t0)/(te - t0)) * 1/(te - t0)**order
        return yd


class HarmonicTrajectory(Trajectory):
    """
    This generator provides a scalar harmonic cosine signal
    with derivatives up to order 4
    """
    # TODO provide formula up to order n
    public_settings = OrderedDict([("Amplitude", 0.25),
                                   ("Frequency", 0.1),
                                   ("Offset", 0.75)])

    def __init__(self, settings):
        Trajectory.__init__(self, settings)
        assert(settings["differential_order"] <= 4)

    def _desired_values(self, t):
        yd = []

        a = self._settings['Amplitude']
        f = self._settings['Frequency']
        off = self._settings["Offset"]
        
        # i need sin for a test
        # yd.append(a * np.cos(2 * np.pi * f * t))
        # yd.append(-a * 2 * np.pi * f * np.sin(2 * np.pi * f * t))
        # yd.append(-a * (2 * np.pi * f) ** 2 * np.cos(2 * np.pi * f * t))
        # yd.append(a * (2 * np.pi * f) ** 3 * np.sin(2 * np.pi * f * t))
        # yd.append(a * (2 * np.pi * f) ** 4 * np.cos(2 * np.pi * f * t))

        yd.append(a * np.sin(2 * np.pi * f * t) + off)
        yd.append(a * 2 * np.pi * f * np.cos(2 * np.pi * f * t))
        yd.append(-a * (2 * np.pi * f) ** 2 * np.sin(2 * np.pi * f * t))
        yd.append(-a * (2 * np.pi * f) ** 3 * np.cos(2 * np.pi * f * t))
        yd.append(a * (2 * np.pi * f) ** 4 * np.sin(2 * np.pi * f * t))

        return [y for idx, y in enumerate(yd) if idx <= self._settings["differential_order"]]

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
    last_u = 0

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=len(self.public_settings["input_state"]))
        settings.update(input_type="system_state")
        Controller.__init__(self, settings)

        # define variables for data saving in the right dimension
        self.e_old = np.zeros(len(self._settings["input_state"]))
        self.integral_old = np.zeros(len(self._settings["input_state"]))

    def _control(self, is_values, desired_values, t):
        # input abbreviations
        x = np.zeros(len(self._settings["input_state"]))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx] = is_values[int(state)]

        yd = desired_values

        # step size
        dt = t - self.last_time
        # save current time
        self.last_time = t

        if dt != 0:
            for i in range(len(x)):
                # error
                e = yd[i] - x[i]
                integral = e*dt + self.integral_old[i]
                if integral > self._settings["output_limits"][1]:
                    integral = self._settings["output_limits"][1]
                elif integral < self._settings["output_limits"][0]:
                    integral = self._settings["output_limits"][0]
                differential = (e - self.e_old)/dt

                output = self._settings["Kp"]*e\
                         + self._settings["Ki"]*integral \
                         + self._settings["Kd"]*differential

                if output > self._settings["output_limits"][1]:
                    output = self._settings["output_limits"][1]
                elif output < self._settings["output_limits"][0]:
                    output = self._settings["output_limits"][0]

                # save data for new calculation
                self.e_old[i] = e
                self.integral_old[i] = integral
            u = output
        else:
            u = self.last_u
        self.last_u = u
        return u

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
        vals = np.array(signal_values)
        return np.sum(vals, 0)


# TODO Limiter

# register all generic modules
pm.register_simulation_module(Solver, ODEInt)
pm.register_simulation_module(Trajectory, SmoothTransition)
pm.register_simulation_module(Trajectory, PolynomialTrajectory)
pm.register_simulation_module(Trajectory, HarmonicTrajectory)
pm.register_simulation_module(Controller, PIDController)
pm.register_simulation_module(ModelMixer, AdditiveMixer)
pm.register_simulation_module(ObserverMixer, AdditiveMixer)
