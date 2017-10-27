# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict

import pymoskito as pm

#settings
g = 9.81             # gravity [m/s^2]
#cart
M  = 4.2774          # mass [kg]
D = 10               # friction constant [Ns/m]
#pendulum
m = 0.3211           # mass [kg]
d = 0.023            # friction constant [Nms]
l = 0.3533           # length [m]
J = 0.072            # moment of intertia [kg*m^2]

#class begin
class BasicController(pm.Controller):
     """
     A linear Controller, stabilizing the in phi=PI linearized system
     """
     public_settings = OrderedDict([("poles",[-1,-2,-3,-4]),
                                    ("source","system_state"),
                                    ("tick divider", 1)
                                    ])

#init
     def __init__(self,settings):
        settings.update(input_order=0)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
    
#matrices
        # the system matrices after linearization in phi=PI
        z = (M+m)*J - (m*l)**2
        self._A = np.array([[0,0,1,0],
                            [0,0,0,1],
                            [0,(m*l)**2*g/z,-J*D/z,m*l*d/z],
                            [0,-(M+m)*m*l*g/z,m*l*D/z,-(M+m)*d/z]
                           ])
        self._B = np.array([[0],
                            [0],
                            [J/z],
                            [-l*m/z]
                           ])
        self._C = np.array([[1, 0, 0, 0]])
        # the equilibrium state as a vector
        self._eq_state = np.array([0,np.pi,0,0])

#calculations
        # pole placement of linearized state feedback
        self._K = pm.controltools.place_siso(self._A, self._B, self._settings["poles"])
        self._V = pm.controltools.calc_prefilter(self._A, self._B, self._C, self._K)
#control
     def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):

        x = np.copy(input_values) - self._eq_state
        yd = trajectory_values
        output = - np.dot(self._K, x) + np.dot(self._V, yd[0])
        
        return output
#register
pm.register_simulation_module(pm.Controller, BasicController)
