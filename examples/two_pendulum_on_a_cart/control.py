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
                                   ('poles', [-8+7j, -8-7j, -3+3j, -3-3j, -1.7+2j, -1.7-2j]),
                                   # ('poles', [-7.2+0.22j, -7.2-0.22j, -4.2, -3.87, -1.6, -1.27]),
                                   ('equilibrium', [0, 0, np.pi, 0, np.pi, 0]),
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
        self.A = symcalc.A_func(list(self._settings['equilibrium']), parameter)
        self.B = symcalc.B_func(list(self._settings['equilibrium']), parameter)
        self.C = symcalc.C
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)
        print "K: ", self.K
        print "V: ", self.V

    def _control(self, is_values, desired_values, t):
        # input abbreviations
        x = is_values
        yd = desired_values

        u = - np.dot(self.K, x) + np.dot(self.V, yd[0,0])

        # temp
        if u > 60:
            u = 60
        if u < -60:
            u = -60


        return u

pm.register_simulation_module(Controller, LinearStateFeedback)
