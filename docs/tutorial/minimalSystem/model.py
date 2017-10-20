# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm

#settings
initial_state = [0, 180.0, 0, 0]
g = 9.81             # gravity [m/s^2]
#cart
M  = 4.2774          # mass [kg]
D = 10               # friction constant [Ns/m]
#pendulum
m = 0.3211           # mass [kg]
d = 0.023            # friction constant [Nms]
l = 0.3533           # length [m]
J = 0.072            # moment of intertia [kg*m^2]

#class
class RodPendulumModel(pm.Model):
    public_settings = OrderedDict([("initial state", initial_state),
                                   ("cart mass", M),
                                   ("cart friction",D),
                                   ("pendulum mass", m),
                                   ("pendulum intertia", J),
                                   ("pendulum friction", d),
                                   ("pendulum length",l),
                                   ("gravity", g)])
#init
    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][1] = np.deg2rad(settings["initial state"][1])
        settings["initial state"][3] = np.deg2rad(settings["initial state"][3])

        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "cart position", "Unit": "m"},
            1: {"Name": "pendulum angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.M = self._settings["cart mass"]
        self.D = self._settings["cart friction"]
        self.m = self._settings["pendulum mass"]
        self.J = self._settings["pendulum intertia"]
        self.d = self._settings["pendulum friction"]
        self.l = self._settings["pendulum length"]
        self.g = self._settings["gravity"]
#state
    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        # definitional
        s    = x[0]
        phi  = x[1]
        ds   = x[2]
        dphi = x[3]
        F    = args[0]
		
        dx1 = ds
        dx2 = dphi
        dx3 = (J*F - J*D*ds - m*l*J*dphi**2*np.sin(phi) + (m*l)**2*g*np.sin(phi)*np.cos(phi) - m*l*d*dphi*np.cos(phi)) \
               / ((M+m)*J - (m*l*np.cos(phi))**2)
        dx4 = (m*l*np.cos(phi)*F - m*l*D*ds*np.cos(phi) - (m*l*dphi)**2*np.cos(phi)*np.sin(phi) + (M+m)*m*l*g*np.sin(phi) - (M+m)*d*dphi)\
               / ((M+m)*J - (m*l*np.cos(phi))**2)

        dx = np.array([dx1,dx2,dx3,dx4])
        return dx
#root
    def root_function(self, x):
        return [False]
    def check_consistency(self, x):
        pass
#output
    def calc_output(self, input):
        """
        return cart position as output
        """
        return np.array([input[0]], dtype=float)
#register
pm.register_simulation_module(pm.Model, RodPendulumModel)
