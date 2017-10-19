# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm

initial_state = [0, 180.0, 0, 0]

g = 9.81             # gravity [m/s^2]
#cart
M  = 4.2774          # mass [kg]
d0 = 10              # friction constant [Ns/m]
#pendulum
m  = 0.3211          # mass [kg]
d1 = 0.023           # friction constant [Nms]
l = 0.3533           # length [m]
J = 0.072            # moment of intertia [kg*m^2]

class RodPendulumModel(pm.Model):
    public_settings = OrderedDict([("initial state", initial_state),
                                   ("cart mass", M),("cart friction",d0),("pendulum mass", m),
                                   ("pendulum intertia", J),("pendulum friction", d1),
								   ("pendulum length",l),("gravity", g)])

    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][1] = np.deg2rad(settings["initial state"][1])
        settings["initial state"][3] = np.deg2rad(settings["initial state"][3])

        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.M = self._settings["cart mass"]
        self.d0 = self._settings["cart friction"]
        self.m = self._settings["pendulum mass"]
        self.J = self._settings["pendulum intertia"]
        self.d1 = self._settings["pendulum friction"]
        self.l = self._settings["pendulum length"]
        self.g = self._settings["gravity"]

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
        u = args[0][0]

        dx1 = ds
        dx2 = dphi
        dx3 = (self.g*self.m*phi - self.d0*ds + self.d1*dphi/self.l+ u)/self.M		
        dx4 = (-self.g*(self.M+self.m)*phi + self.d0*ds - (self.d1*(self.M+self.m))/(self.l1*self.m)*dphi - u)/(self.M*self.l)

        dx = np.array([[dx1],[dx2],[dx3],[dx4]])
        return dx

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        pass

    def calc_output(self, input):
        """
        return cart position as output
        """
        return np.array([input[0]], dtype=float)

pm.register_simulation_module(pm.Model, RodPendulumModel)
