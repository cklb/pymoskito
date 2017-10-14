# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm

#from . import settings as mp

initial_state = [0, 180.0, 0, 0]

# pendulum
m1 = 358.3 / 1000.0  # kg
a1 = 0.43  # m --> determined by experiments
J1 = 0.0379999429  # Nms**2
d1 = 0.0058885212  # Nms

m0 = 3.340  # kg - weight of the cart

g = 9.81  # m/s**2 - gravity

class RodPendulumModel(pm.Model):
    """
    Implementation of the rod pendulum on a cart system
    """
#    public_settings = OrderedDict([("initial state", mp.initial_state),
#                                   ("m0", mp.m0),
#                                   ("m1", mp.m1),
#                                   ("a1", mp.a1),
#                                   ("J1", mp.J1),
#                                   ("d1", mp.d1),
#                                   ("g", mp.g),
#                                   ])
    public_settings = OrderedDict([("initial state", initial_state),
                                   ("m0", m0),
                                   ("m1", m1),
                                   ("a1", a1),
                                   ("J1", J1),
                                   ("d1", d1),
                                   ("g", g),
                                   ])

    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][1] = np.deg2rad(settings["initial state"][1])
        settings["initial state"][3] = np.deg2rad(settings["initial state"][3])

        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.m0 = self._settings["m0"]

        self.m1 = self._settings["m1"]
        self.a1 = self._settings["a1"]
        self.J1 = self._settings["J1"]
        self.d1 = self._settings["d1"]

        self.g = self._settings["g"]

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        # definitional
        s = x[0]
        phi = x[1]
        ds = x[2]
        dphi = x[3]
        acc = args[0][0]

        dx1 = ds
        dx2 = dphi
        dx3 = acc
        dx4 = (self.a1*self.g*self.m1*np.sin(phi) - self.d1*dphi)/(self.J1 + self.a1**2*self.m1) \
              + self.a1*self.m1*np.cos(phi)*acc/(self.J1 + self.a1**2*self.m1)

        dx = np.array([[dx1],
                       [dx2],
                       [dx3],
                       [dx4]])
        return dx

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        """
        Check something
        """
        pass

    def calc_output(self, input):
        """
        return cart position as output
        :param input: input values
        :return: cart position
        """
        return np.array([input[0]], dtype=float)


pm.register_simulation_module(pm.Model, RodPendulumModel)
