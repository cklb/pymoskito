# -*- coding: utf-8 -*-

from collections import OrderedDict
from pymoskito.simulation_modules import Controller
from pymoskito.tools import get_coefficients

import settings as st
import symcalculation as symcalc


class ExactInputOutputLinearization(Controller):
    """
    controller which use the flatness virtue of the system
    """
    # TODO check this class on 'array unification'
    public_settings = OrderedDict([("poles", [-3.1, -3.1, -3.1, -3.1]),
                                  ("tick divider", 1)])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=4)
        settings.update(input_type="system_state")

        Controller.__init__(self, settings)

        # run pole placement
        self.k = get_coefficients(self._settings["poles"])[0]

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):
        # input abbreviations
        x = input_values
        yd = trajectory_values

        # time constant and damping ratio depend on state x2
        if x[1] < 0:
            T = st.T_n
            d = st.d_n
        else:
            T = st.T_p
            d = st.d_p

        y_d0 = x[2]
        y_d1 = x[3]
        parameter = [x[0], x[1], x[2], x[3], T, d, st.k_s, st.k_L, st.k_V, st.A_B, st.A_Sp, st.m, st.g]
        y_d2 = symcalc.y_d2_func(*parameter)
        y_d3 = symcalc.y_d3_func(*parameter)

        LgLf3h = symcalc.LgLf3h_func(*parameter)
        Lf4h = symcalc.Lf4h_func(*parameter)

        # calculate fictional input v
        v = (yd[4]
             + self.k[3] * (yd[3] - y_d3)
             + self.k[2] * (yd[2] - y_d2)
             + self.k[1] * (yd[1] - y_d1)
             + self.k[0] * (yd[0] - y_d0))
        u = (v - Lf4h)/LgLf3h
        
        return u


class OpenLoop(Controller):
    """
    manual pwm input
    """
    # TODO check this class on 'array unification'
    public_settings = OrderedDict([("pwm", 220),
                                   ("tick divider", 1)])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        Controller.__init__(self, settings)

    def _control(self, time, trajectory_values=None, feedforward_values=None, input_values=None, **kwargs):

        u = self._settings["pwm"]
        return u
