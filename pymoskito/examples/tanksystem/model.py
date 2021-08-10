from collections import OrderedDict

import numpy as np

import pymoskito as pm
from . import settings as st


class TwoTankSystem(pm.Model):
    public_settings = OrderedDict([('initial state', st.initial_states),
                                   ("AT", st.AT),
                                   ("hT", st.hT),
                                   ("AS1", st.AS1),
                                   ("AS2", st.AS2),
                                   ("g", st.g),
                                   ("K", st.K)])

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
        uA = args[0].squeeze()

        if x1 < 0:
            x1 = 0
        if x2 < 0:
            x2 = 0

        g = self.settings['g']
        K = self.settings['K']
        AS1 = self.settings['AS1']
        AS2 = self.settings['AS2']
        AT = self.settings['AT']

        dx1 = - AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2)) + K / AT * uA
        dx2 = AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2)) - AS2 / AT * np.sqrt(2 * g * x2)

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
        return [input_vector[0], input_vector[1] + np.random.random(1)[0] / 100]


pm.register_simulation_module(pm.Model, TwoTankSystem)
