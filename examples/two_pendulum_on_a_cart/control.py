# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict
import pymoskito.registry as pm
from pymoskito.simulation_modules import Controller

import settings as st
import symbolic_calculation as symcalc
import pymoskito.tools as to

# this package enable the inclusion of c-code
import ctypes as ct


class LinearStateFeedback(Controller):

    public_settings = OrderedDict([('poles', [-9, -7, -4, -2, -3, -2]),
                                   ("long pendulum", "u"),
                                   ("short pendulum", "o"),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        eq_state = calc_equilibrium(settings)
        # pole placement
        parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
        self.A = symcalc.A_func(list(eq_state), parameter)
        self.B = symcalc.B_func(list(eq_state), parameter)
        self.C = symcalc.C
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)
        # eig = np.linalg.eig(self.A - np.dot(self.B, self.K))
        print "equilibrium: ", eq_state
        print "poles: ", self._settings['poles']
        print "K: ", self.K.tolist()[0]
        print "V: ", self.V

    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values

        if eq is None:
            eq = calc_closest_eq_state(self._settings, is_values)
        x = x - np.atleast_2d(eq).T

        # this is a second version
        # x = calc_small_signal_state(self._settings, is_values)

        # u corresponds to a force [kg*m/s**2] = [N]
        u = - np.dot(self.K, x) + np.dot(self.V, yd[0, 0])

        return u


class LinearStateFeedbackParLin(Controller):

    public_settings = OrderedDict([('poles', [-9, -7, -4, -2, -3, -2]),
                                   ("long pendulum", "u"),
                                   ("short pendulum", "o"),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        eq_state = calc_equilibrium(settings)
        # pole placement
        parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
        self.A = symcalc.A_func_par_lin(list(eq_state), parameter)
        self.B = symcalc.B_func_par_lin(list(eq_state), parameter)
        self.C = symcalc.C_par_lin
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)
        # eig = np.linalg.eig(self.A - np.dot(self.B, self.K))
        print "equilibrium: ", eq_state
        print "poles: ", self._settings['poles']
        print "K: ", self.K
        print "V: ", self.V

    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values

        if eq is None:
            eq = calc_closest_eq_state(self._settings, is_values)
        x = x - np.atleast_2d(eq).T

        # this is a second version
        # x = calc_small_signal_state(self._settings, is_values)

        # u corresponds to a acceleration [m/s**2]
        u = - np.dot(self.K, x) + np.dot(self.V, yd[0, 0])

        return u


class CLinearStateFeedback(Controller):

    public_settings = OrderedDict([('equilibrium', 4),
                                   ('debug1', 8),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        # load dll, the calling convention is cdecl
        self.lib = ct.cdll.TestLib
        print self.lib

        # create c compatible variables
        self.c_time = ct.c_float(0)
        self.c_pos_arr = (ct.c_float*3)()
        self.c_long_arr = (ct.c_float*3)()
        self.c_short_arr = (ct.c_float*3)()
        self.c_motor_voltage = ct.c_float(0)
        self.c_u_ret = ct.c_float(0)
        self.c_k = (ct.c_float*6)()
        for idx, val in enumerate([0]*6):
            self.c_k[idx] = val
        self.c_equilibrium = ct.c_uint8(self._settings["equilibrium"])
        self.c_debug1 = ct.c_float(self._settings["debug1"])
        self.c_debug2 = ct.c_float(0)
        self.c_debug_arr = (ct.c_float*6)()
        for idx, val in enumerate([0]*6):
            self.c_debug_arr[idx] = val

    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values
        self.c_time = ct.c_float(t)
        self.c_pos_arr[0] = x[0, 0]
        self.c_pos_arr[1] = x[1, 0]
        self.c_pos_arr[2] = 0
        self.c_long_arr[0] = x[2, 0]*(180/np.pi)
        self.c_long_arr[1] = x[3, 0]*(180/np.pi)
        self.c_long_arr[2] = 0
        self.c_short_arr[0] = x[4, 0]*(180/np.pi)
        self.c_short_arr[1] = x[5, 0]*(180/np.pi)
        self.c_short_arr[2] = 0

        err = self.lib.control_loop(self.c_time,
                                    ct.byref(self.c_pos_arr),
                                    ct.byref(self.c_long_arr),
                                    ct.byref(self.c_short_arr),
                                    self.c_motor_voltage,
                                    ct.byref(self.c_u_ret),
                                    ct.byref(self.c_k),
                                    self.c_equilibrium,
                                    ct.byref(self.c_debug1),
                                    ct.byref(self.c_debug2),
                                    ct.byref(self.c_debug_arr))

        u = np.array([[self.c_u_ret.value]])
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
            E1 = 0.5*st.m1*st.l1**2*x4**2 + st.m1*st.g*st.l1*(np.cos(x3) + 1)
        elif self._settings["long pendulum"] == "o":
            E1 = 0.5*st.m1*st.l1**2*x4**2 + st.m1*st.g*st.l1*(np.cos(x3) - 1)

        if self._settings["short pendulum"] == "u":
            E2 = 0.5*st.m2*st.l2**2*x6**2 + st.m2*st.g*st.l2*(np.cos(x5) + 1)
        elif self._settings["short pendulum"] == "o":
            E2 = 0.5*st.m2*st.l2**2*x6**2 + st.m2*st.g*st.l2*(np.cos(x5) - 1)

        G = st.m0*x2*E0 + st.m1*st.l1*x4*np.cos(x3)*E1 + st.m2*st.l2*x6*np.cos(x5)*E2*self.w**2

        u_lja = -self._settings["k"]*G  # + (st.d1*E1*x4**2 + st.d2*E2*x6**2)/G

        # the u of the ljapunov method is a acceleration and the model require a force
        d0 = 0
        d1 = 0
        d2 = 0
        M1_star = 0
        M2_star = 0

        M = st.m0 + st.m1*(np.sin(x3))**2 + st.m2*(np.sin(x5))**2
        F1 = st.m1*np.sin(x3)*(st.g*np.cos(x3) - st.l1*x4**2)
        F2 = st.m2*np.sin(x5)*(st.g*np.cos(x5) - st.l2*x6**2)
        u = - F1 - F2 + u_lja*M + d0*x2 - (M1_star - d1*x4)*np.cos(x3)/st.l1 - (M2_star - d2*x6)*np.cos(x5)/st.l2

        return u

class CLjapunovController(Controller):

    public_settings = OrderedDict([('equilibrium', 3),
                                   ('k', 8),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        # load dll, the calling convention is cdecl
        self.lib = ct.cdll.TestLib

        # create c compatible variables
        self.c_time = ct.c_float(0)
        self.c_pos_arr = (ct.c_float*3)()
        self.c_long_arr = (ct.c_float*3)()
        self.c_short_arr = (ct.c_float*3)()
        self.c_motor_voltage = ct.c_float(0)
        self.c_u_ret = ct.c_float(0)
        self.c_k = (ct.c_float*6)()
        for idx, val in enumerate([0]*6):
            self.c_k[idx] = val
        self.c_equilibrium = ct.c_uint8(self._settings["equilibrium"])
        self.c_debug1 = ct.c_float(0)
        self.c_debug2 = ct.c_float(0)
        self.c_debug_arr = (ct.c_float*6)()
        for idx, val in enumerate([0]*6):
            self.c_debug_arr[idx] = val
        self.c_gain = ct.c_float(self._settings["k"])

    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values
        self.c_time = ct.c_float(t)
        self.c_pos_arr[0] = x[0, 0]
        self.c_pos_arr[1] = x[1, 0]
        self.c_pos_arr[2] = 0
        self.c_long_arr[0] = x[2, 0]*(180/np.pi)
        self.c_long_arr[1] = x[3, 0]*(180/np.pi)
        self.c_long_arr[2] = 0
        self.c_short_arr[0] = x[4, 0]*(180/np.pi)
        self.c_short_arr[1] = x[5, 0]*(180/np.pi)
        self.c_short_arr[2] = 0

        err = self.lib.control_loop(self.c_time,
                                    ct.byref(self.c_pos_arr),
                                    ct.byref(self.c_long_arr),
                                    ct.byref(self.c_short_arr),
                                    self.c_motor_voltage,
                                    ct.byref(self.c_u_ret),
                                    ct.byref(self.c_k),
                                    self.c_equilibrium,
                                    ct.byref(self.c_debug1),
                                    ct.byref(self.c_debug2),
                                    ct.byref(self.c_debug_arr),
                                    ct.byref(self.c_gain))

        u = np.array([[self.c_u_ret.value]])
        return u


class SwingUpController(Controller):

    public_settings = OrderedDict([
        ("k", 8),
        ("long pendulum", "u"),
        ("short pendulum", "o"),
        ("poles", [-10.1, -8.2, -6.9, -5, -2.5, -1.5]),
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


class SwingUpController2(Controller):
    """
    This class realise the swing up for equilibria with a arbitrary
    amount of turns of the pendulums

    The swing up of both pendulums require a adjustment of the
    integrator settings to
    rTol: 1e-09
    aTol: 1e-11
    """

    public_settings = OrderedDict([
        ("k", 10),
        ("long pendulum", "u"),
        ("short pendulum", "o"),
        ("poles", [-9, -7, -4, -2, -3, -2]),
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

        settings.update({"equilibrium": calc_equilibrium(settings)})
        settings.update(self.module_settings)
        settings["type"] = "LinearStateFeedback"
        self.linear_state_feedback = LinearStateFeedback(settings)

        self.switch = False

    def _control(self, is_values, desired_values, t):
        x1, x2, x3, x4, x5, x6 = is_values

        # looking for the closest equilibrium
        eq_state = calc_closest_eq_state(self._settings, is_values)

        # we have to check several conditions
        #          phi1                  phi1_d
        a = (-0.2 + eq_state[2] <= x3 <= 0 + eq_state[2]) and (-0.2 <= x4 <= 0.5)
        #           phi2                 phi2_d
        b = (-0.2 + eq_state[4] <= x5 <= 0 + eq_state[4]) and (-0.2 <= x6 <= 0.5)
        #        phi1                  phi1_d
        c = (0 + eq_state[2] <= x3 <= 0.2 + eq_state[2]) and (-0.5 <= x4 <= 0.2)
        #          phi2                   phi2_d
        d = (0 + eq_state[4] <= x5 <= 0.2 + eq_state[4]) and (-0.5 <= x6 <= 0.2)

        eq_oo = False
        eq_ou = False
        eq_uo = False

        if self._settings["long pendulum"] == "o":
            eq_ou = True
        if self._settings["short pendulum"] == "o":
            eq_uo = True

        if eq_ou and eq_uo:
            eq_oo = True
            eq_ou = False
            eq_uo = False

        if (eq_oo and a and b)or (eq_oo and c and d) or (eq_ou and a) or (eq_ou and c) or (eq_uo and b) or (eq_uo and d):
            self.switch = True
        else:
            # this adjustment is only gut feeling
            e = (-0.3 + eq_state[2] <= x3 <= 0.3 + eq_state[2])
            f = (-0.3 + eq_state[4] <= x5 <= 0.3 + eq_state[4])
            if not (e and f):
                self.switch = False

        # print "t: ", t, "Switch: ", self.switch

        if self.switch:
            u = self.linear_state_feedback._control(is_values, desired_values, t, eq=eq_state)
        else:
            u = self.ljapunov._control(is_values, desired_values, t)

        return u


class CSwingUpController2(Controller):

    public_settings = OrderedDict([('equilibrium', 4),
                                   ('gain', 8),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        # load dll, the calling convention is cdecl
        self.lib = ct.cdll.TestLib
        print self.lib

        # create c compatible variables
        self.c_time = ct.c_float(0)
        self.c_pos_arr = (ct.c_float*3)()
        self.c_long_arr = (ct.c_float*3)()
        self.c_short_arr = (ct.c_float*3)()
        self.c_motor_voltage = ct.c_float(0)
        self.c_u_ret = ct.c_float(0)
        self.c_k = (ct.c_float*6)()
        for idx, val in enumerate([0]*6):
            self.c_k[idx] = val
        self.c_equilibrium = ct.c_uint8(self._settings["equilibrium"])
        self.c_debug1 = ct.c_float(0)
        self.c_debug2 = ct.c_float(0)
        self.c_debug_arr = (ct.c_float*6)()
        self.c_gain = ct.c_float(self._settings["gain"])
        for idx, val in enumerate([0]*6):
            self.c_debug_arr[idx] = val

    def _control(self, is_values, desired_values, t, eq=None):
        # input abbreviations
        x = is_values
        yd = desired_values
        self.c_time = ct.c_float(t)
        self.c_pos_arr[0] = x[0, 0]
        self.c_pos_arr[1] = x[1, 0]
        self.c_pos_arr[2] = 0
        self.c_long_arr[0] = x[2, 0]*(180/np.pi)
        self.c_long_arr[1] = x[3, 0]*(180/np.pi)
        self.c_long_arr[2] = 0
        self.c_short_arr[0] = x[4, 0]*(180/np.pi)
        self.c_short_arr[1] = x[5, 0]*(180/np.pi)
        self.c_short_arr[2] = 0

        err = self.lib.control_loop(self.c_time,
                                    ct.byref(self.c_pos_arr),
                                    ct.byref(self.c_long_arr),
                                    ct.byref(self.c_short_arr),
                                    self.c_motor_voltage,
                                    ct.byref(self.c_u_ret),
                                    ct.byref(self.c_k),
                                    self.c_equilibrium,
                                    ct.byref(self.c_debug1),
                                    ct.byref(self.c_debug2),
                                    ct.byref(self.c_debug_arr),
                                    ct.byref(self.c_gain))

        u = np.array([[self.c_u_ret.value]])
        return u

pm.register_simulation_module(Controller, LinearStateFeedback)
pm.register_simulation_module(Controller, LinearStateFeedbackParLin)
pm.register_simulation_module(Controller, CLinearStateFeedback)
pm.register_simulation_module(Controller, LjapunovController)
pm.register_simulation_module(Controller, CLjapunovController)
pm.register_simulation_module(Controller, SwingUpController)
pm.register_simulation_module(Controller, SwingUpController2)
pm.register_simulation_module(Controller, CSwingUpController2)


def calc_equilibrium(settings):
    equilibrium = np.zeros(6)
    if settings["long pendulum"] == "u":
        equilibrium[2] = np.pi
    if settings["short pendulum"] == "u":
        equilibrium[4] = np.pi

    return equilibrium


def calc_closest_eq_state(settings, state):
    # looking for the closest equilibrium for the two pendulums
    phi1 = float(state[2])
    phi2 = float(state[4])

    # consider the multiple pendulum states, because of the continuously angle
    # pendulum is on top: phi_eq = 2*PI*k
    # pendulum is at the bottom: phi_eq = (2*k + 1)*PI

    # pendulum 1 (long) is on top
    k1o = int(phi1/(2*np.pi))
    if (abs(phi1) % (2*np.pi)) > np.pi:
        k1o = k1o + np.sign(phi1)

    # pendulum 1 (long) is at the bottom
    k1u = int((phi1-np.pi)/(2*np.pi))
    if (abs(phi1 - np.pi) % (2*np.pi)) > np.pi:
        k1u = k1u + np.sign(phi1)

    # pendulum 2 (short) is on top
    k2o = int(phi2/(2*np.pi))
    if (abs(phi2) % (2*np.pi)) > np.pi:
        k2o = k2o + np.sign(phi2)

    # pendulum 2 (short) is at the bottom
    k2u = int((phi2 - np.pi)/(2*np.pi))
    if (abs(phi2 - np.pi) % (2*np.pi)) > np.pi:
        k2u = k2u + np.sign(phi2)

    eq_state = np.zeros(6)
    if settings["long pendulum"] == "o":
        eq_state[2] = 2*np.pi*k1o
    if settings["long pendulum"] == "u":
        eq_state[2] = (2*k1u + 1)*np.pi
    if settings["short pendulum"] == "o":
        eq_state[4] = 2*np.pi*k2o
    if settings["short pendulum"] == "u":
        eq_state[4] = (2*k2u + 1)*np.pi

    return eq_state


def calc_small_signal_state(settings, state):

    phi1 = (abs(state[2][0]) % (2*np.pi))*np.sign(state[2][0])
    phi2 = (abs(state[4][0]) % (2*np.pi))*np.sign(state[4][0])

    # transform the angle of the pendulums into an interval from -pi to +pi
    # pendulum 1 (long) is on top
    phi1_o = phi1
    if abs(phi1_o) > np.pi:
        phi1_o -= np.sign(state[2][0])*2*np.pi

    # pendulum 2 (short) is on top
    phi2_o = phi2
    if abs(phi2_o) > np.pi:
        phi2_o -= np.sign(state[4][0])*2*np.pi

    # transform the angle of the pendulums into an interval from 0 to 2pi
    # pendulum 1 (long) is at the bottom
    phi1_u = phi1
    if phi1_u < 0:
        phi1_u -= np.sign(state[2][0])*2*np.pi

    # pendulum 2 (short) is at the bottom
    phi2_u = phi2
    if phi2_u < 0:
        phi2_u -= np.sign(state[4][0])*2*np.pi

    # calc small signal state
    small_signal_state = np.zeros((6, 1))
    for idx, val in enumerate(state):
        small_signal_state[idx, 0] = val[0]

    if settings["long pendulum"] == "o":
        small_signal_state[2][0] = phi1_o - 0
    if settings["long pendulum"] == "u":
        small_signal_state[2][0] = phi1_u - np.pi
    if settings["short pendulum"] == "o":
        small_signal_state[4][0] = phi2_o - 0
    if settings["short pendulum"] == "u":
        small_signal_state[4][0] = phi2_u - np.pi

    return small_signal_state




