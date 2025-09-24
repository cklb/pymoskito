from collections import OrderedDict

import numpy as np

import pymoskito as pm
from . import settings as st


class TwoTankSystem(pm.Model):
    public_settings = OrderedDict([('initial state', st.initial_states),
                                   ("hT", st.hT),
                                   ("hV", st.hV),
                                   ("AS1", st.AS1),
                                   ("AS2", st.AS2),
                                   ("AT1", st.AT1),
                                   ("AT2", st.AT2),
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

        # register events
        self.register_event(self.event_level_1_low)
        self.register_event(self.event_level_2_low)
        self.register_event(self.event_level_1_high)
        self.register_event(self.event_level_2_high)

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
        g = self.settings['g']
        K = self.settings['K']
        AS1 = self.settings['AS1']
        AS2 = self.settings['AS2']
        AT1 = self.settings['AT1']
        AT2 = self.settings['AT2']
        hT = self.settings["hT"]
        hV = self.settings["hV"]
        a1 = AS1 * np.sqrt(2 * g / (AT1 ** 2 - AS1 ** 2))
        a2 = AS2 * np.sqrt(2 * g / (AT2 ** 2 - AS2 ** 2))

        dx = np.zeros(2)
        if x1 < hT:
            # tank 1 not full, count inflow
            dx[0] += K / AT1 * uA
        if x1 >= 0 and x2 < hT:
            # tank 1 not empty and tank 2 not full, count out- and inflow
            dx[0] -= a1 * np.sqrt(x1 + hV)
            dx[1] += a1 * np.sqrt(x1 + hV)
        if x2 >= 0:
            # tank not empty, count outflow
            dx[1] -= a2 * np.sqrt(x2 + hV)

        return dx

    def event_level_1_low(self, t, x):
        return x[0]

    def event_level_2_low(self, t, x):
        return x[1]

    def event_level_1_high(self, t, x):
        return x[0] - self.settings["hT"]

    def event_level_2_high(self, t, x):
        return x[1] - self.settings["hT"]

    def calc_output(self, input_vector):
        return input_vector


pm.register_simulation_module(pm.Model, TwoTankSystem)
