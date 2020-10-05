import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class TwoTankSystem(pm.Model):
    public_settings = OrderedDict([('initial state', [0, 0]),
                                   ("AT1", st.AT1),
                                   ("AT2", st.AT2),
                                   ("hT1", st.hT1),
                                   ("hT2", st.hT2),
                                   ("hV1", st.hV1),
                                   ("hV2", st.hV2),
                                   ("AS1", st.AS1),
                                   ("AS2", st.AS2),
                                   ("g", st.g),
                                   ("Ku", st.Ku),
                                   ("uA0", st.uA0)])

    def __init__(self, settings):  # Constructor
        # add specific "private" settings
        settings.update(state_count=2)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "Level Tank1", "Unit": "m"},
            1: {"Name": "Level Tank2", "Unit": "m"},
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
        AS1 = self.settings['AS1']
        AS2 = self.settings['AS2']
        AT1 = self.settings['AT1']
        AT2 = self.settings['AT2']
        hV1 = self.settings['hV1']
        hV2 = self.settings['hV2']

        a1 = AS1 * np.sqrt(2 * g / (AT1 ** 2 - AS1 ** 2))
        a2 = AS2 * np.sqrt(2 * g / (AT2 ** 2 - AS2 ** 2))

        if x1 <= 1e-6:
            hV1 = 0.0

        if x2 <= 1e-6:
            hV2 = 0.0

        if uA < uA0:
            u = np.array([0])
        else:
            u = uA - uA0

        dx1 = - a1 * np.sign(x1 + hV1) * np.sqrt(np.abs(x1 + hV1)) + Ku / AT1 * u
        dx2 = - a2 * np.sign(x2 + hV2) * np.sqrt(np.abs(x2 + hV2)) + \
              a1 * np.sign(x1 + hV1) * np.sqrt(np.abs(x1 + hV1)) * AT1 / AT2

        return np.array([dx1, dx2])

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

        if x[1] <= 0:
            x0[1] = 0
            flag = True

        return flag, x0

    def calc_output(self, input_vector):
        return [input_vector[0] + np.random.random(1)[0] / 100, input_vector[1]]


pm.register_simulation_module(pm.Model, TwoTankSystem)
