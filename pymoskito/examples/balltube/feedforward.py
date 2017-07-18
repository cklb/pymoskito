# -*- coding: utf-8 -*-

import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class BallInTubeFeedforward(pm.Feedforward):
    """
    Calculate flatness based feedforward.

    The flat output is given by the ball position (x3)
    x1_flat and x2_flat are the system states expressed in flat coordinates.
    """
    public_settings = OrderedDict([("tick divider", 1)])

    def __init__(self, settings):
        settings.update(input_order=4)
        settings.update(output_dim=1)
        pm.Feedforward.__init__(self, settings)

    def _feedforward(self, time, trajectory_values):

        yd = trajectory_values
        x1_flat = (np.sqrt((yd[2] + st.g)*st.m*st.A_Sp**2/st.k_L)
                   + st.A_B*yd[1])/st.k_V
        x2_flat = (yd[3]*st.m*st.A_Sp**2/(2*st.k_V*st.k_L*(st.k_V*x1_flat
                                                           - st.A_B*yd[1]))
                   + st.A_B*yd[2]/st.k_V)

        # feed forward control
        u = (st.T**2*(yd[4]*st.m*st.A_Sp**2 - 2*st.k_L*(st.k_V*x2_flat
                                                        - st.A_B*yd[2])**2)
             / (2*st.k_s*st.k_V*st.k_L*(st.k_V*x1_flat - st.A_B*yd[1]))
             + (st.T**2*st.A_B*yd[3])/(st.k_s*st.k_V)
             + (2*st.d*st.T*x2_flat)/st.k_s
             + x1_flat/st.k_s)*(255/st.Vcc)

        return np.array([[u]], dtype=float)

pm.register_simulation_module(pm.Feedforward, BallInTubeFeedforward)
