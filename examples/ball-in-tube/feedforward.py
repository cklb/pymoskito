__author__ = 'christoph'

from collections import OrderedDict
import pymoskito.pymoskito as pm
from pymoskito.simulation_modules import Feedforward
import numpy as np
import settings as st


class BallInTubeFeedforward(Feedforward):
    """
    calculate feedforward, based on the flatness of the system
    """

    public_settings = OrderedDict([("tick divider", 1)])

    def __init__(self, settings):
        settings.update(input_order=4)
        settings.update(output_dim=1)
        Feedforward.__init__(self, settings)

    def _feedforward(self, traj_values):

        yd = traj_values
        x1_flat = (np.sqrt((yd[2] + st.g)*st.m*st.A_Sp**2/st.k_L) + st.A_B*yd[1])/st.k_V
        x2_flat = yd[3]*st.m*st.A_Sp**2/(2*st.k_V*st.k_L*(st.k_V*x1_flat - st.A_B*yd[1])) + st.A_B*yd[2]/st.k_V

        # time constant and damping ratio depend on state x2
        if x2_flat < 0:
            T = st.T_n
            d = st.d_n
        else:
            T = st.T_p
            d = st.d_p

        # feed forward control
        u = (T**2*(yd[4]*st.m*st.A_Sp**2 - 2*st.k_L*(st.k_V*x2_flat - st.A_B*yd[2])**2)\
            / (2*st.k_s*st.k_V*st.k_L*(st.k_V*x1_flat - st.A_B*yd[1]))\
            + (T**2*st.A_B*yd[3])/(st.k_s * st.k_V)\
            + (2*d*T*x2_flat)/st.k_s\
            + x1_flat/st.k_s)*(255/12)

        return np.array([u])

pm.register_simulation_module(Feedforward, BallInTubeFeedforward)
