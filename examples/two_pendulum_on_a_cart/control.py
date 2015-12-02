# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict
import pymoskito.pymoskito as pm
from pymoskito.simulation_modules import Controller

import settings as st
import symbolic_calculation as symcalc
import pymoskito.tools as to


class LinearStateFeedback(Controller):

    public_settings = OrderedDict([('poles', [-10.1,-8.2,-6.9,-5,-2.5,-1.5]),
                                   ('rest position', [0, 0, 0, 0, 0, 0]),
                                   ('tick divider', 1)])

    def __init__(self, settings):
        # add specific private settings
        settings.update(input_order=1)
        settings.update(ouput_dim=1)
        settings.update(input_type='system_state')

        Controller.__init__(self, settings)

        # pole placement
        parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
        self.A = symcalc.A_func(list(self._settings['rest position']), parameter)
        self.B = symcalc.B_func(list(self._settings['rest position']), parameter)
        self.C = symcalc.C
        self.K = to.ackerSISO(self.A, self.B, self._settings['poles'])
        self.V = to.calc_prefilter(self.A, self.B, self.C, self.K)

    def _control(self, is_values, desired_values, t):
        # input abbreviations
        x = is_values
        yd = desired_values

        u = - np.dot(self.K, x) + np.dot(yd, self.V)

        return u

pm.register_simulation_module(Controller, LinearStateFeedback)
