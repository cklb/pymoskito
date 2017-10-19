# -*- coding: utf-8 -*-
import numpy as np
import copy
from collections import OrderedDict

import pymoskito as pm

class BasicController(pm.Controller):
     """

     """
	public_settings = ([("poles",[-1,-2,-3,-4]),
                        ("source","system state"),
                        ("steady state", [0,180,0,0])
                        ("tick divider", 1)
                       ])
						
	def __init__(self,settings):
        settings.update(input_order=0)
		settings.update(output_dim=1)
		settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((1, ))
		
	def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
		f = [3.6971,-4.9286,-2.3740,-11.4855]
		x = input_values 
		v = 1
		yd = trajectory_values
		#u = f*x + v*yd
		self._output = x[0]*f[0] + x[1]*f[1] + x[2]*f[2] + x[3]*f[3] + v*yd[0]
		
		return self._output
	
pm.register_simulation_module(pm.Controller, BasicController)
