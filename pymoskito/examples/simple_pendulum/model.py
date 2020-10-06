# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm


# class
class PendulumModel(pm.Model):
    public_settings = OrderedDict([("initial state", [0, 180.0, 0, 0]),
                                   ("cart mass", 4.3),  # [kg]
                                   ("cart friction", 10),  # [Ns/m]
                                   ("pendulum mass", 0.32),  # [kg]
                                   ("pendulum inertia", 0.07),  # [kg*m^2]
                                   ("pendulum friction", 0.03),  # [Nms]
                                   ("pendulum length", 0.35),  # [m]
                                   ("gravity", 9.81)])  # [m/s^2]

    # init
    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][1] = np.deg2rad(settings["initial state"][1])
        settings["initial state"][3] = np.deg2rad(settings["initial state"][3])

        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        settings.update({"output_info": {0: {"Name": "cart position",
                                             "Unit": "m"}}})
        pm.Model.__init__(self, settings)

    # state
    def state_function(self, t, x, args):
        # definitional
        s = x[0]
        phi = x[1]
        ds = x[2]
        dphi = x[3]
        F = args[0].squeeze()

        # shortcuts for readability
        M = self._settings["cart mass"]
        D = self._settings["cart friction"]
        m = self._settings["pendulum mass"]
        J = self._settings["pendulum inertia"]
        d = self._settings["pendulum friction"]
        l = self._settings["pendulum length"]
        g = self._settings["gravity"]

        dx1 = ds
        dx2 = dphi
        dx3 = ((J * F
                - J * D * ds
                - m * l * J * dphi ** 2 * np.sin(phi)
                + (m * l) ** 2 * g * np.sin(phi) * np.cos(phi)
                - m * l * d * dphi * np.cos(phi))
               / ((M + m) * J - (m * l * np.cos(phi)) ** 2))
        dx4 = ((m * l * np.cos(phi) * F
                - m * l * D * ds * np.cos(phi)
                - (m * l * dphi) ** 2 * np.cos(phi) * np.sin(phi)
                + (M + m) * m * l * g * np.sin(phi) - (M + m) * d * dphi)
               / ((M + m) * J - (m * l * np.cos(phi)) ** 2))

        dx = np.array([dx1, dx2, dx3, dx4])
        return dx

    # output
    def calc_output(self, input_vector):
        return input_vector[0]
