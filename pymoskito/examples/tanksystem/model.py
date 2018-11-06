import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class TankModel(pm.Model):
    public_settings = OrderedDict([('initial state', [0, 0]),
                                   ("AT1", st.AT),
                                   ("hT1", st.hT),
                                   ("hV1", st.hV),
                                   ("AS1", st.AS),
                                   ("g", st.g),
                                   ("Ku", st.Ku),
                                   ("uA0", st.uA0)])

    def __init__(self, settings):  # Constructor
        # add specific "private" settings
        settings.update(state_count=1)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "Füllstand Tank", "Unit": "m"},
        }})
        pm.Model.__init__(self, settings)

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input u
        """
        x1 = x[0]
        x2 = x[1]
        uA = args[0]

        uA0 = self.settings['uA0']
        g = self.settings['g']
        Ku = self.settings['Ku']
        AS = self.settings['AS']
        AT = self.settings['AT']
        hV = self.settings['hV']

        a1 = AS * np.sqrt(2 * g / (AT ** 2 - AS ** 2))

        if uA < uA0:
            u = np.array([0])
        else:
            u = uA - uA0

        if x1 <= 0:
            hV = 0

        dx1 = - a1 * np.sign(x1 + hV) * np.sqrt(np.abs(x1 + hV)) + Ku / AT * u

        return np.array([dx1])

    def root_function(self, x):
        """
        in this case this means zero crossing detection for the water height elevation.
        :param x: state
        """
        x0 = x
        flag = False

        if x[0] <= 0:
            x0[0] = 0
            flag = True

        return flag, x0

    def calc_output(self, input_vector):
        return [input_vector[0]]


pm.register_simulation_module(pm.Model, TankModel)
