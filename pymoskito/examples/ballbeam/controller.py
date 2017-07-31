# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict

import pymoskito as pm
import pymoskito.controltools

from . import settings as st
from .linearization import linearise_system


class FController(pm.Controller):
    """
    Controller created by changing f(x)
    """
    public_settings = OrderedDict([("poles", [-3.1, -3.1, -3.1, -3.1]),
                                   ("source", "system_state"),
                                   ("tick divider", 1),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))

        # run pole placement
        self.K = pymoskito.controltools.char_coefficients(self._settings["poles"])

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        x1, x2, x3, x4 = input_values
        yd = trajectory_values

        # calculate nonlinear terms phi
        phi1 = x1
        phi2 = x2
        phi3 = -st.B*st.G*np.sin(x3)
        phi4 = -st.B*st.G*x4*np.cos(x3)

        # calculate fictional input v
        v = (yd[4]
             + self.K[3] * (yd[3] - phi4)
             + self.K[2] * (yd[2] - phi3)
             + self.K[1] * (yd[1] - phi2)
             + self.K[0] * (yd[0] - phi1)
             )

        # calculate a(x)
        a = -st.B*st.G*np.cos(x3)
        # calculate b(x)
        b = st.B*st.G*x4**2*np.sin(x3)
        
        # calculate u
        u = (v-b)/a

        # transform back
        self._output = (u * (st.M*x1**2 + st.J + st.Jb)
                        + st.M*(2*x1*x2*x4 + st.G*x1*np.cos(x3)))
        
        return self._output


class GController(pm.Controller):
    """
    Controller created by changing g(x)
    """
    public_settings = OrderedDict([("poles", [-2.8, -2.8, -2.8, -2.8]),
                                   ("source", "system_state"),
                                   ("tick divider", 1),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))

        # run pole placement
        self.K = pm.char_coefficients(self._settings["poles"])

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        x = input_values
        yd = trajectory_values

        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]
        phi3 = -st.B*st.G*np.sin(x[2]) + st.B*x[0]*x[3]**2
        phi4 = -st.B*st.G*x[3]*np.cos(x[2]) + st.B*x[1]*x[3]**2

        # calculate fictional input v
        v = (yd[4]
             + self.K[3] * (yd[3] - phi4)
             + self.K[2] * (yd[2] - phi3)
             + self.K[1] * (yd[1] - phi2)
             + self.K[0] * (yd[0] - phi1)
             )

        # calculate a(x)
        a = -st.B*st.G*np.cos(x[2]) + 2*st.B*x[1]*x[3]

        # calculate b(x)
        b = st.B**2*x[0]*x[3]**4 + st.B*st.G*(1 - st.B)*x[3]**2*np.sin(x[2])

        # calculate u
        u = (v-b)/a
        return u


class JController(pm.Controller):
    """
    Controller based on the standard jacobian approximation.
    """
    public_settings = OrderedDict([("poles", [-2, -2, -2, -2]),
                                   ("source", "system_state"),
                                   ("tick divider", 1),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))

        # run pole placement
        self.K = pm.char_coefficients(self._settings["poles"])

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        x = input_values
        yd = trajectory_values

        # calculate linear terms phi
        phi1 = x[0]
        phi2 = x[1]
        phi3 = -st.B*st.G*x[2]
        phi4 = -st.B*st.G*x[3]

        # calculate fictional input v
        v = (yd[4]
             + self.K[3] * (yd[3] - phi4)
             + self.K[2] * (yd[2] - phi3)
             + self.K[1] * (yd[1] - phi2)
             + self.K[0] * (yd[0] - phi1)
             )

        # calculate a(x)
        a = -st.B*st.G/(st.J + st.Jb)

        # calculate b(x)
        b = st.B*st.M*st.G**2*x[0]/(st.J + st.Jb)

        # calculate u
        u = (v-b)/a
        return u


class LSSController(pm.Controller):
    r"""
    Linear state space controller
    
    This controller is based on the linearized system. The steady state is
    given by :math:`(\boldsymbol{x}^e, \tau^e)` .
    """
    public_settings = OrderedDict([("poles", [-3.1, -3.1, -3.1, -3.1]),
                                   ("source", "system_state"),
                                   ("steady state", [0, 0, 0, 0]),
                                   ("steady tau", 0),
                                   ("tick divider", 1)
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))

        # run pole placement
        a_mat, b_mat, c_mat = linearise_system(self._settings["steady state"],
                                               self._settings["steady tau"])
        self.K = pm.place_siso(a_mat, b_mat, self._settings["poles"])
        self.V = pm.calc_prefilter(a_mat, b_mat, c_mat, self.K)

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        yd = trajectory_values

        self._output = -self.K @ input_values + yd[0]*self.V
        return self._output


class PIXController(pm.Controller):
    r"""
    Linear statespace controller
    
    This controller is based on the linearized system, extended with an 
    integrator. The steady state is
    given by :math:`(\boldsymbol{x}^e, \tau^e)` .
    """
    public_settings = OrderedDict([("poles", [-3.1, -3.1, -3.1, -3.1]),
                                   ("source", "system_state"),
                                   ("steady state", [0, 0, 0, 0]),
                                   ("steady tau", 0),
                                   ("step width", .01),
                                   ('Ki', -4),
                                   ("I Limit", 0.1),
                                   ("tick divider", 1)
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._error = 0
        self._output = np.zeros((1, ))

        # run pole placement
        a_mat, b_mat, c_mat = linearise_system(self._settings["steady state"],
                                               self._settings["steady tau"])
        self.K = pm.place_siso(a_mat, b_mat, self._settings["poles"])
        self.V = pm.calc_prefilter(a_mat, b_mat, c_mat, self.K)
        self.h = self._settings["tick divider"] * self._settings["step width"]

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        x = input_values
        yd = trajectory_values

        e = self._error + self.h * (yd[0] - x[0])

        # saturate error
        if not abs(e) > self._settings["I Limit"]:
            self._error = e

        # calculate u
        u = -self.K @ x + yd[0]*self.V + self._settings["Ki"] * self._error
        return u

pm.register_simulation_module(pm.Controller, FController)
pm.register_simulation_module(pm.Controller, GController)
pm.register_simulation_module(pm.Controller, JController)
pm.register_simulation_module(pm.Controller, LSSController)
pm.register_simulation_module(pm.Controller, PIXController)
