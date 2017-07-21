# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm

from . import settings as st


class CarModel(pm.Model):
    public_settings = OrderedDict([('initial state', st.initial_state),
                                   ("d1", st.d1),
                                   ("l2", st.l2),
                                   ("d2", st.d2),
                                   ("l3", st.l3),
                                   ("dia", st.dia),
                                   ("car_radius", st.car_radius),
                                   ("wheel", st.wheel),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=5)
        settings.update(input_count=2)
        settings.update({"output_info": {
            0: {"Name": "x-position", "Unit": "m"},
            1: {"Name": "y-position", "Unit": "m"},
            2: {"Name": "car-angle", "Unit": "rad"},
            3: {"Name": "1st-trailer-angle", "Unit": "rad"},
            4: {"Name": "2nd-trailer-angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.d1 = self._settings['d1']
        self.l2 = self._settings['l2']
        self.d2 = self._settings['d2']
        self.l3 = self._settings['l3']

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        x1, x2, x3, x4, x5 = x
        v, w = 1, 1

        return np.array([v * np.cos(x3),
                         v * np.sin(x3),
                         w,
                         v / self.l2 * np.sin(x3 - x4) - self.d1 / self.l2 * w * np.cos(x3 - x4),
                         v * (1 / self.l3 * np.sin(x3 - x5) - (self.d2 + self.l2) / (self.l2 * self.l3) * np.sin(
                             x3 - x4) * np.cos(x4 - x5)) \
                         + w * (-self.d1 / self.l3 * np.cos(x3 - x5) + (self.d1 * (self.l2 + self.d2)) / (
                             self.l2 * self.l3) * np.cos(x3 - x4) * np.cos(x4 - x5))
                         ])

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        pass

    def calc_output(self, input):
        return input

pm.register_simulation_module(pm.Model, CarModel)
