# -*- coding: utf-8 -*-
import numpy as np
import copy
from collections import OrderedDict

import pymoskito as pm

from python.rod_pendulum import model_parameter as mp
from . import symbolic_calculation as symcalc


class LinearStateFeedback(pm.Controller):

    public_settings = OrderedDict([
        ("poles", [-3.5+1.2*1j, -3.5-1.2*1j, -3.3 + 3.4*1j, -3.3 - 3.4*1j]),
        ("eq_state", [0, 180, 0, 0]),
        ("tick divider", 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=0)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        pm.Controller.__init__(self, settings)

        settings["eq_state"][1] = np.deg2rad(settings["eq_state"][1])
        settings["eq_state"][3] = np.deg2rad(settings["eq_state"][3])
        self.eq_state = settings["eq_state"]
        # pole placement
        parameter = [mp.m0, mp.m1, mp.a1, mp.l1, mp.J1, mp.d1, mp.g]
        self.A = symcalc.A_func(list(self.eq_state), parameter)
        self.B = symcalc.B_func(list(self.eq_state), parameter)
        self.C = symcalc.C
        self.K = pm.tools.place_siso(self.A, self.B, self._settings['poles'])
        self.V = pm.tools.calc_prefilter(self.A, self.B, self.C, self.K)
        # eig = np.linalg.eig(self.A - np.dot(self.B, self.K))

        self._logger.info("Equilibrium: {}".format(self.eq_state))
        self._logger.info("Poles: {}".format(self._settings["poles"]))
        self._logger.info("K: {}".format(self.K[0]))
        self._logger.info("V: {}".format(self.V[0]))

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        # input abbreviations
        x = copy.deepcopy(input_values)
        yd = trajectory_values
        eq = kwargs.get("eq", None)

        if eq is None:
            eq = calc_closest_eq_state(self._settings, input_values)

        x = x - np.atleast_2d(eq).T

        # u corresponds to a acceleration [m/s**2]
        u = - np.dot(self.K, x) + np.dot(self.V, yd[0, 0])

        return u


class LjapunovController(pm.Controller):

    public_settings = OrderedDict([
        ("k", 1),
        ("k1", 0),
        ("k2", 0),
        ("eps", 1e-2),
        ("tick divider", 1)])

    term_old = 0
    u_old = 0

    def __init__(self, settings):
        settings.update(input_order=0)
        settings.update(output_order=1)
        settings.update(input_type="system_state")
        pm.Controller.__init__(self, settings)

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        s, varphi1, sdot, varphidot1 = input_values

        # # paper variant
        # Eo = mp.a1*mp.g*mp.m1
        # E = 0.5*mp.J1*varphidot1**2 \
        #     + 0.5*mp.a1**2*mp.m1*varphidot1**2 \
        #     + mp.a1*mp.g*mp.m1*np.cos(varphi1) \
        #     - mp.a1*mp.m1*sdot*varphidot1*np.cos(varphi1) \
        #     + 0.5*mp.m0*sdot**2 \
        #     + 0.5*mp.m1*sdot**2
        #
        # term = (E-Eo)*((mp.m0 + mp.m1)*sdot
        #                - mp.a1*mp.m1*varphidot1*np.cos(varphi1)
        #                - mp.m1*mp.a1*np.cos(varphi1)
        #                + (mp.a1**2*mp.m1**2*sdot*np.cos(varphi1)**2)/(mp.J1 + mp.a1**2*mp.m1)) \
        #        - self._settings["kd"]*sdot

        # own variant
        E0 = 0.5*mp.m0*sdot**2 + 0.5*self._settings["k1"]*s**2
        E1 = 0.5*(mp.J1 + mp.a1**2*mp.m1)*varphidot1**2 + mp.a1*mp.g*mp.m1*(np.cos(varphi1) - 1)

        term = E0*mp.m0*sdot + E1*mp.a1*mp.m1*varphidot1*np.cos(varphi1)

        # trial to swing-up the pendulum with friction
        # if abs(term) >= self._settings["eps"]:
        #     u_lja = -self._settings["k"]*term + (E1*mp.d1*varphidot1**2 - E0*self._settings["k1"]*s*sdot)/term
        #     self.u_old = u_lja
        # else:
        #     u_lja = self.u_old

        u_lja = -self._settings["k"]*term

        return u_lja


class SwingUpController(pm.Controller):
    """
    This class realise the swing up for equilibria with a arbitrary
    amount of turns of the pendulums
    """

    public_settings = OrderedDict([
        ("k", 5),
        ("k1", 0),
        ("k2", 0),
        ("eps", 1e-3),
        ("poles", [-3.5, -3.5, -2+1j, -2-1j]),
        ("eq_state", [0, 0, 0, 0]),
        ("tick divider", 1)
    ])

    def __init__(self, settings):
        settings.update(input_order=0)
        settings.update(output_order=1)
        settings.update(input_type="system_state")
        self.module_settings = {"modules": settings["modules"]}  # save module settings
        pm.Controller.__init__(self, settings)

        # add dict with module information, because it was deleted in the base class
        settings.update(self.module_settings)
        settings["type"] = "LjapunovController"
        self.ljapunov = LjapunovController(settings)

        settings.update(self.module_settings)
        settings["type"] = "LinearStateFeedback"
        self.linear_state_feedback = LinearStateFeedback(settings)

        self.switch = False

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        s, varphi1, sdot, varphidot1 = input_values

        # looking for the closest equilibrium
        eq = calc_closest_eq_state(self._settings, input_values)

        # check switching condition
        self.switch = check_switchover(input_values, eq)

        # print("t: {}, Switch: {}".format(time, self.switch))

        if self.switch:
            u = self.linear_state_feedback._control(time,
                                                    trajectory_values,
                                                    input_values=input_values,
                                                    eq=eq)
        else:
            u = self.ljapunov._control(time,
                                       trajectory_values,
                                       input_values=input_values)

        return u


class SwingUpSlaveController(pm.Controller):

    public_settings = OrderedDict([
        ("k0", 35),
        ("k1", 10),
        ("poles", [-3.5, -3.5, -2+1j, -2-1j]),
        ("eq_state", [0, 0, 0, 0]),
        ("s after swing-up", 0),
        ("tick divider", 1)
    ])

    def __init__(self, settings):
        settings.update(input_order=2)
        settings.update(output_order=1)
        settings.update(input_type="system_state")
        self.module_settings = {"modules": settings["modules"]}  # save module settings
        pm.Controller.__init__(self, settings)

        # add dict with module information, because it was deleted in the base class
        settings.update(self.module_settings)
        settings["type"] = "LinearStateFeedback"
        self.linear_state_feedback = LinearStateFeedback(settings)

        # rewrite setting input_order from LinearStateFeedback
        settings.update(input_order=2)

        self.switch = False

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        s, varphi1, sdot, varphidot1 = input_values[:, 0]

        # looking for the closest equilibrium
        eq = calc_closest_eq_state(self._settings, input_values)

        # check switching condition
        self.switch = check_switchover(input_values, eq)

        print("t: {}, Switch: {}".format(time, self.switch))

        if self.switch:
            u = self.linear_state_feedback._control(time,
                                                    np.array([[self._settings["s after swing-up"]]]),
                                                    input_values=input_values,
                                                    eq=eq)
        else:
            y_ref_d0 = trajectory_values[0][0]
            y_ref_d1 = trajectory_values[0][1]
            y_ref_d2 = trajectory_values[0][2]

            u = y_ref_d2 + self._settings["k1"]*(y_ref_d1 - sdot) + self._settings["k0"]*(y_ref_d0 - s)

        return u


def calc_closest_eq_state(settings, state):
    # looking for the closest equilibrium for the rod pendulum
    phi = float(state[1])

    # consider the multiple pendulum states, because of the continuously angle
    # pendulum is on top: phi_eq = 2*PI*k
    # pendulum is at the bottom: phi_eq = (2*k + 1)*PI

    # rod pendulum is on top
    ko = int(phi/(2*np.pi))
    if (abs(phi) % (2*np.pi)) > np.pi:
        ko += np.sign(phi)

    # rod pendulum is at the bottom
    ku = int((phi-np.pi)/(2*np.pi))
    if (abs(phi - np.pi) % (2*np.pi)) > np.pi:
        ku += np.sign(phi)

    eq_state = np.zeros(4)
    if settings["eq_state"][1] == 0:  # rod pendulum on the top
        eq_state[1] = 2*np.pi*ko
    elif settings["eq_state"][1] == np.pi:  # rod pendulum on the bottom
        eq_state[1] = (2*ku + 1)*np.pi
    else:
        raise Exception("Equilibrium State in Settings is not valid!!!")

    return eq_state


def check_switchover(state, eq):
    """
    activate linear state feedback control or other control laws (future) to stabilise the pendulums,
    if the following conditions are True
    """
    varphi1 = state[1]
    varphidot1 = state[3]

    # we have to check several conditions
    a = (-0.2 + eq[1] <= varphi1 <= 0 + eq[1]) and (-0.2 <= varphidot1 <= 0.5)
    b = (0 + eq[1] <= varphi1 <= 0.2 + eq[1]) and (-0.5 <= varphidot1 <= 0.2)

    if a or b:
        return True
    # else:
    #     # this adjustment is only gut feeling
    #     c = (-0.3 + eq[2] <= varphi1 <= 0.3 + eq[2])
    #     if c:
    #         return True

    return False

pm.register_simulation_module(pm.Controller, LinearStateFeedback)
pm.register_simulation_module(pm.Controller, LjapunovController)
pm.register_simulation_module(pm.Controller, SwingUpController)
pm.register_simulation_module(pm.Controller, SwingUpSlaveController)
