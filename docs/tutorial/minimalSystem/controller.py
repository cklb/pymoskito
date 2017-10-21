# -*- coding: utf-8 -*-
import numpy as np
import copy
from collections import OrderedDict

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

class BasicController(pm.Controller):
     """
     A linear Controller, stabilizing the in phi=180 linearized 
     """
     public_settings = OrderedDict([("poles",[-1,-2,-3,-4]),
                                    ("source","system_state"),
                                    ("tick divider", 1)
                                    ])

     def __init__(self,settings):
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type=settings["source"])
        # controller only stabilizes in this equilibrium state, 
		# therefore changing this setting is suppressed
        settings.update(eq_state=[0,180,0,0])
		
        settings["eq_state"][1] = np.deg2rad(settings["eq_state"][1])
        settings["eq_state"][3] = np.deg2rad(settings["eq_state"][3])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))
		
        # the System after linearization in phi=180
        self.A = np.array([[0,0,1,0],
                           [0,0,0,1],
                           [0,g*m/M,-D/M,d/(l*M)],
                           [0,-g/l*(1+m/M),D/(l*M),-d*(M+m)/(l**2*m*M)]
                          ])
        self.B = np.array([[0],
                           [0],
                           [1/M],
                           [-1/(l*M)]
                          ])
        self.C = np.array([[1, 0, 0, 0]])
		
		# make the equlibrium state a vector
        self.eq_state = np.array(self._settings["eq_state"])
		
        # pole placement of linearized state feedback
        self.K = pm.controltools.place_siso(self.A, self.B, self._settings["poles"])
        self.V = pm.controltools.calc_prefilter(self.A, self.B, self.C, self.K)

     def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        #f = [3.6971,-4.9286,-2.3740,-11.4855]
        #v = 21.19873634 #f[0]
        #x = np.copy(input_values) 
		#subtraction of equilibrium, since controller only stabilizes x=[0,0,0,0]
        #x[1] = x[1] - np.pi
        x = np.copy(input_values) - self.eq_state
        yd = trajectory_values
        #self._output = - np.dot(f, x) + np.dot(v, yd[0])
        self._output = - np.dot(self.K, x) + np.dot(self.V, yd[0])
        
        return self._output

pm.register_simulation_module(pm.Controller, BasicController)
