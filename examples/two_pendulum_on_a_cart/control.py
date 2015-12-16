# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict
import pymoskito.pymoskito as pm
from pymoskito.simulation_modules import Controller

import settings as st
import symbolic_calculation as symcalc
import pymoskito.tools as to


class LinearStateFeedback(Controller):

    public_settings = OrderedDict([#('poles', [-1,-1,-1,-1,-1,-1]),
                                   ('poles', [-10.1,-8.2,-6.9,-5,-2.5,-1.5]),
                                   # ('poles', [-2+1j, -2-1j, -2, -4, -3+1.8j, -3-1.8j]),
                                   # ('poles', [-8+7j, -8-7j, -3.5, -3, -1.7+1j, -1.7-1j]),
                                   # ('poles', [-1+4.5j, -1-4.5j, -5, -7, -4, -3.5]),
                                   # ('poles', [-8+7j, -8-7j, -3+3j, -3-3j, -1.7+2j, -1.7-2j]),
                                   # ('poles', [-7.2+0.22j, -7.2-0.22j, -4.2, -3.87, -1.6, -1.27]),
                                   # ('poles', [-8+7j, -8-7j, -1.7+1j, -1.7-1j, -3.5, -3.0]),
                                   ('equilibrium', [0, 0, 3.141592653589793, 0, 3.141592653589793, 0]),
                                   # ('equilibrium', [0, 0, 0, 0, 0, 0]),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        # pole placement
        parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
        self.A = symcalc.A_func(list(self._settings["equilibrium"]), parameter)
        self.B = symcalc.B_func(list(self._settings["equilibrium"]), parameter)
        self.C = symcalc.C
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)
        eig = np.linalg.eig(self.A - np.dot(self.B, self.K))
        print "equilibrium: ", self._settings["equilibrium"]
        print "poles: ", self._settings['poles']
        print "K: ", self.K
        print "V: ", self.V


    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values

        if eq is None:
            eq = self._settings["equilibrium"]
        x = x - np.atleast_2d(eq).T

        u = - np.dot(self.K, x) + np.dot(self.V, yd[0,0])


        return u

class LjapunovController(Controller):

    public_settings = OrderedDict([
        ("k", 8),
        ("long pendulum", "u"),
        ("short pendulum", "o"),
        ("tick divider", 1)])

    def __init__(self, settings):
        settings.update(input_order=0)
        settings.update(output_order=1)
        settings.update(input_type="system_state")
        Controller.__init__(self, settings)

        self.w = st.m1*st.l1/(st.m2*st.l2)

    def _control(self, is_values, desired_values, t):
        x1, x2, x3, x4, x5, x6 = is_values

        E0 = 0.5*st.m0*x2**2
        E1 = 0
        E2 = 0

        if self._settings["long pendulum"] == "u":
            E1 = 0.5*st.J1_real*x4**2 + st.m1*st.g*st.l1*(np.cos(x3) + 1)
        elif self._settings["long pendulum"] == "o":
            E1 = 0.5*st.J1_real*x4**2 + st.m1*st.g*st.l1*(np.cos(x3) - 1)

        if self._settings["short pendulum"] == "u":
            E2 = 0.5*st.J2_real*x6**2 + st.m2*st.g*st.l2*(np.cos(x5) + 1)
        elif self._settings["short pendulum"] == "o":
            E2 = 0.5*st.J2_real*x6**2 + st.m2*st.g*st.l2*(np.cos(x5) - 1)

        G = st.m1*st.l1*x4*np.cos(x3)*E1 + st.m2*st.l2*x6*np.cos(x5)*E2*self.w**2 +st.m0*x2*E0

        u = -self._settings["k"]*G # + (st.d1*E1*x4**2 + st.d2*E2*x6**2)/G

        # linear_state_feedback = LinearStateFeedback()

        return u


class SwingUpController(Controller):

    public_settings = OrderedDict([
        ("k", 8),
        ("long pendulum", "u"),
        ("short pendulum", "o"),
        ("poles", [-10.1,-8.2,-6.9,-5,-2.5,-1.5]),
        ("tick divider", 1)
    ])

    def __init__(self, settings):
        settings.update(input_order=0)
        settings.update(output_order=1)
        settings.update(input_type="system_state")
        self.module_settings = {"modules": settings["modules"]}
        Controller.__init__(self, settings)

        # add dict with module information, because it was deleted in the base class
        settings.update(self.module_settings)
        settings["type"] = "LjapunovController"
        self.ljapunov = LjapunovController(settings)

        self.eq_state = np.zeros(6)
        if settings["long pendulum"] == "u":
            self.eq_state[2] = np.pi
        elif settings["short pendulum"] == "u":
            self.eq_state[4] = np.pi
        settings.update({"equilibrium": self.eq_state})
        settings.update(self.module_settings)
        settings["type"] = "LinearStateFeedback"
        self.linear_state_feedback = LinearStateFeedback(settings)

        self.switch = False

    def _control(self, is_values, desired_values, t):
        x1, x2, x3, x4, x5, x6 = is_values

        # consider the multiple pendulum states, because of the continuously angle
        n = int(x3/(2*np.pi))
        if x3%(2*np.pi) > np.pi and n > 0:
            n += 1
        if x3%(2*np.pi) < np.pi and n < 0:
            n -= 1
        m = int(x5/(2*np.pi))
        if x5%(2*np.pi) > np.pi and m > 0:
            m += 1
        if x5%(2*np.pi) < np.pi and m < 0:
           m -= 1

        # we have to check several conditions
        #          phi1                  phi1_d
        a = (-0.2 + 2*n*np.pi <= x3 <= 0 + 2*n*np.pi) and (-0.2 <= x4 <= 0.5)
        #           phi2                 phi2_d
        b = (-0.2 + 2*m*np.pi <= x5 <= 0 + 2*m*np.pi) and (-0.2 <= x6 <= 0.5)
        #        phi1                  phi1_d
        c = (0 + 2*n*np.pi <= x3 <= 0.2 + 2*n*np.pi) and (-0.5 <= x4 <= 0.2)
        #          phi2                   phi2_d
        d = (0 + 2*m*np.pi <= x5 <= 0.2 + 2*m*np.pi) and (-0.5 <= x6 <= 0.2)

        Roo = False
        Rou = False
        Ruo = False

        if self._settings["long pendulum"] == "o":
            Rou = True
            self.eq_state[2] = 2*n*np.pi
        if self._settings["short pendulum"] == "o":
            Ruo = True
            self.eq_state[4] = 2*m*np.pi

        if Rou and Ruo:
            Roo = True
            Rou = False
            Ruo = False
            self.eq_state[2] = 2*n*np.pi
            self.eq_state[4] = 2*m*np.pi

        if (Roo and a and b)or (Roo and c and d) or (Rou and a) or (Rou and c) or (Ruo and b) or (Ruo and d):
            self.switch = True

        if self.switch:
            u = self.linear_state_feedback._control(is_values, desired_values, t, eq=self.eq_state)
        else:
            u = self.ljapunov._control(is_values, desired_values, t)

        return u

pm.register_simulation_module(Controller, LinearStateFeedback)
pm.register_simulation_module(Controller, LjapunovController)
pm.register_simulation_module(Controller, SwingUpController)
