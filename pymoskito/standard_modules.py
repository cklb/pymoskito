__author__ = 'stefan'
"""
ready to go implementations of generic simulation modules
"""

from scipy.integrate import ode
import sympy as sp
import numpy as np
from collections import OrderedDict
from simulation_modules import Model, Solver, Trajectory


class ODEInt(Solver):
    """
    Wrapper for ode_int from Scipy project
    """
    public_settings = OrderedDict([
        ("Mode", "vode"),
        ("Method", "adams"),
        ("measure rate", 1e2),
        ("step size", 1e-3),
        ("rTol", 1e-6),
        ("aTol", 1e-9),
        ("start time", 0),
        ("end time", 5),
        ("initial state", [0, 0, 0, 0])
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
        self._solver.set_initial_value(self._settings["initial state"])

    @property
    def t(self):
        return self._solver.t

    def set_input(self, *args):
        """
        propagate input changes to ode_int
        """
        self._solver.set_f_params(args)

    def integrate(self, t):
        """
        integrates until target step reached
        :param t: target time
        :return: system state at target time
        """
        state = self._solver.integrate(t + self._settings["step size"])
        if self._model.root_function(state):
            # reset solver since discontinuous change in equations happened
            self._solver.set_initial_value(state, self.t)
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

        # differentiate phi(tau) index in list corresponds to order
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


class HarmonicTrajectory(Trajectory):
    """
    This generator provides a scalar harmonic cosine signal
    with derivatives up to order 4
    """
    # TODO provide formula up to order n
    public_settings = OrderedDict([("Amplitude", 0.5),
                                   ("Frequency", 5)])

    def __init__(self, settings):
        Trajectory.__init__(self, settings)
        assert(settings["differential_order"] <= 4)

    def _desired_values(self, t):
        yd = []

        a = self._settings['Amplitude']
        f = self._settings['Frequency']

        yd.append(a * np.cos(2 * np.pi * f * t))
        yd.append(-a * 2 * np.pi * f * np.sin(2 * np.pi * f * t))
        yd.append(-a * (2 * np.pi * f) ** 2 * np.cos(2 * np.pi * f * t))
        yd.append(a * (2 * np.pi * f) ** 3 * np.sin(2 * np.pi * f * t))
        yd.append(a * (2 * np.pi * f) ** 4 * np.cos(2 * np.pi * f * t))

        return [y for idx, y in enumerate(yd) if idx <= self._settings["differential_order"]]
