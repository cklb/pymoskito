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

        # register events
        self.events = [self.event_level_1_low, self.event_level_2_low,
                       self.event_level_1_high, self.event_level_2_high]

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
        AT = self.settings['AT']

        if x1 < 0:
            # tank empty -> nothing flows out
            dx1 = K / AT * uA
        elif x1 < self.settings["hT"]:
            dx1 = - AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2)) + K / AT * uA
        else:
            # tank full -> nothing flows in
            dx1 = - AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2))

        if x2 < 0:
            # tank empty -> nothing flows out
            dx2 = AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2))
        elif x2 < self.settings["hT"]:
            dx2 = AS1 / AT * np.sign(x1 - x2) * np.sqrt(2 * g * np.abs(x1 - x2)) - AS2 / AT * np.sqrt(2 * g * x2)
        else:
            # tank full -> nothing flows in
            dx2 = - AS2 / AT * np.sqrt(2 * g * x2)

        return np.array([dx1, dx2])

    def event_level_1_low(self, t, x):
        return x[0]

    def event_level_2_low(self, t, x):
        return x[1]

    def event_level_1_high(self, t, x):
        return x[0] - self.settings["hT"]

    def event_level_2_high(self, t, x):
        return x[1] - self.settings["hT"]

    def calc_output(self, input_vector):
        return [input_vector[0], input_vector[1] + np.random.random(1)[0] / 100]


pm.register_simulation_module(pm.Model, TwoTankSystem)
