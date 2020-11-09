# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import numpy as np
import sympy as sp
from sympy.solvers import solve

import pymoskito as pm

import settings as st


class OpenLoop(pm.Controller):
    """
    manual pwm input
    """
    public_settings = OrderedDict([("uA", 10),
                                   ("tick divider", 1)])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        pm.Controller.__init__(self, settings)

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        u = self._settings["uA"]
        return np.array(u)


class CppPIDController(pm.CppBase, pm.Controller):
    """
    PID Controller implemented in cpp with pybind11
    """
    public_settings = OrderedDict([
        ("Kp", 12),
        ("Ti", 12),
        ("Td", 12),
        ("dt [s]", 0.1),
        ("output_limits", [0, 255]),
        ("input_state", [0]),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        m_path = os.path.dirname(__file__)
        if 'tanksystem' not in m_path:
            m_path += '/pymoskito/examples/tanksystem/src/'
        else:
            m_path += '/src/'

        pm.Controller.__init__(self, settings)
        pm.CppBase.__init__(self,
                            module_path=m_path,
                            module_name='Controller',
                            binding_class_name="binding_Controller")

        self.lastTime = 0
        self.lastU = 0

        self.calcLinSys()

        self.pid = self.get_class_from_module().PIDController(self._settings["Kp"],
                                                              self._settings["Ti"],
                                                              self._settings["Td"],
                                                              self._settings["output_limits"][0],
                                                              self._settings["output_limits"][1],
                                                              self._settings['dt [s]'])

    def _control(self,
                 time,
                 trajectory_values=None,
                 feedforward_values=None,
                 input_values=None,
                 **kwargs):
        # step size
        dt = time - self.lastTime

        # input abbreviations
        x = np.zeros((len(self._settings["input_state"]),))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx] = input_values[int(state)]

        if np.isclose(dt, self._settings['dt [s]']):
            # save last control time
            self.lastTime = time

            yd = trajectory_values

            u = self.pid.compute(x, yd)
        else:
            u = self.lastU

        self.lastU = u

        return u


class CppStateController(pm.CppBase, pm.Controller):
    """
    State Controller implemented in cpp with pybind11
    """
    public_settings = OrderedDict([
        ("poles", [-2, -2]),
        ("dt [s]", 0.1),
        ("output_limits", [0, 255]),
        ("input_state", [0]),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        proj_dir = os.path.abspath(os.path.dirname(__file__))
        m_path = os.sep.join([proj_dir, "src"])

        pm.Controller.__init__(self, settings)
        pm.CppBase.__init__(self,
                            module_path=m_path,
                            module_name='Controller',
                            binding_class_name="binding_Controller")

        self.lastTime = 0
        self.lastU = 0

        # pole placement of linearized state feedback
        x10, x20, uA0, A, B, C = self.calcLinSys()
        self._K = pm.controltools.place_siso(A, B, self._settings["poles"])[0]
        self._V = pm.controltools.calc_prefilter(A, B, C, self._K)[0][0]

        self.state = self.get_class_from_module().StateController(self._K,
                                                                  self._V,
                                                                  self._settings["output_limits"][0],
                                                                  self._settings["output_limits"][1])

    def calcLinSys(self):
        x20 = 0.15

        K, AT, Aout1, Aout2, g, x1, x2, uA = sp.symbols('K A_T A_out1 A_out2 g x_1 x_2 u_A')

        # equilibrium
        dx1 = K / AT * uA - Aout1 / AT * sp.sqrt(2 * g * (x1 - x2))
        dx2 = Aout1 / AT * sp.sqrt(2 * g * (x1 - x2)) - Aout2 / AT * sp.sqrt(2 * g * x2)

        x0 = solve([dx1, dx2], [x1, uA], exclude=[K, AT, Aout1, Aout1, x2])[0]

        x10 = x0[0].subs([(K, st.K), (AT, st.AT), (Aout1, st.AS1), (Aout2, st.AS2), (g, st.g), (x2, x20)])
        uA0 = x0[1].subs([(K, st.K), (AT, st.AT), (Aout1, st.AS1), (Aout2, st.AS2), (g, st.g), (x2, x20)])

        subsList = [(K, st.K), (AT, st.AT), (Aout1, st.AS1), (Aout2, st.AS2), (g, st.g), (x2, x20), (x1, x10),
                    (uA, uA0)]
        A = sp.Matrix([[dx1], [dx2]]).jacobian(sp.Matrix([[x1], [x2]])).subs(subsList)
        B = sp.Matrix([[dx1], [dx2]]).jacobian(sp.Matrix([uA])).subs(subsList)
        C = sp.Matrix([0, 1]).T

        return np.array(x10.evalf()).astype(np.float64), \
               x20, \
               np.array(uA0.evalf()).astype(np.float64), \
               np.array(A.evalf()).astype(np.float64), \
               np.array(B.evalf()).astype(np.float64), \
               np.array(C.evalf()).astype(np.float64)

    def _control(self,
                 time,
                 trajectory_values=None,
                 feedforward_values=None,
                 input_values=None,
                 **kwargs):
        # step size
        dt = time - self.lastTime

        # input abbreviations
        x = np.zeros((len(self._settings["input_state"]),))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx] = input_values[int(state)]

        if np.isclose(dt, self._settings['dt [s]']):
            # save last control time
            self.lastTime = time

            yd = trajectory_values

            u = self.state.compute(np.array([x]), np.array([yd]))
        else:
            u = self.lastU

        self.lastU = u

        return u


pm.register_simulation_module(pm.Controller, OpenLoop)
pm.register_simulation_module(pm.Controller, CppPIDController)
pm.register_simulation_module(pm.Controller, CppStateController)
