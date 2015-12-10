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
                                   # ('poles', [-10.1,-8.2,-6.9,-5,-2.5,-1.5]),
                                   # ('poles', [-2+1j, -2-1j, -2, -4, -3+1.8j, -3-1.8j]),
                                   # ('poles', [-8+7j, -8-7j, -3.5, -3, -1.7+1j, -1.7-1j]),
                                   # ('poles', [-1+4.5j, -1-4.5j, -5, -7, -4, -3.5]),
                                   # ('poles', [-8+7j, -8-7j, -3+3j, -3-3j, -1.7+2j, -1.7-2j]),
                                   # ('poles', [-7.2+0.22j, -7.2-0.22j, -4.2, -3.87, -1.6, -1.27]),
                                   ('poles', [-8+7j, -8-7j, -1.7+1j, -1.7-1j, -3.5, -3.0]),
                                   ('equilibrium', [0, 0, 180, 0, 180, 0]),
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
        eq_state = self._settings['equilibrium']
        eq_state[2] = eq_state[2]*np.pi/180
        eq_state[4] = eq_state[4]*np.pi/180
        self.A = symcalc.A_func(list(self._settings['equilibrium']), parameter)
        self.B = symcalc.B_func(list(self._settings['equilibrium']), parameter)
        self.C = symcalc.C
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)
        eig = np.linalg.eig(self.A - np.dot(self.B, self.K))
        print "eq_state: ", eq_state
        print "poles: ", self._settings['poles']
        print "K: ", self.K
        print "V: ", self.V


    def _control(self, is_values, desired_values, t):
        # input abbreviations
        x = is_values
        yd = desired_values

        x = x - np.atleast_2d(self._settings["equilibrium"]).T
        u = - np.dot(self.K, x) + np.dot(self.V, yd[0,0])


        return u

pm.register_simulation_module(Controller, LinearStateFeedback)
