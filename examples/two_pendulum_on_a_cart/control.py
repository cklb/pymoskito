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
        A = symcalc.A_func(list(self._settings['rest position']), parameter)
        B = symcalc.B_func(list(self._settings['rest position']), parameter)
        self.K = to.ackerSISO(A, B, self._settings['poles'])
        self.V = 0

    def _control(self, is_values, desired_values, t):
        # input abbreviations
        x = is_values
        yd = desired_values
        print 'x: ', x, ' type: ', type(x)
        print 'yd: ', yd, ' type: ', type(yd)
        print 'K: ', self.K, ' type: ', type(self.K)

        u = np.dot(-self.K,np.transpose(x))[0,0] + yd[0]*self.V
        return

pm.register_simulation_module(Controller, LinearStateFeedback)