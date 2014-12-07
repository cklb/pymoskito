# -*- coding: utf-8 -*-
"""
Created on Tue Dec 02 21:47:52 2014

@author: cle
"""

import numpy as np

from scipy.integrate import ode
import settings as st

class LuenbergerObserver:
    
        
    
    def __init__(self, linearization):
        self.A = linearization.A
        self.B = linearization.B
        self.C = linearization.C
        self.L = linearization.calcObserver(st.poles_LuenbergerObserver)
        
        self.solver = ode(self.stateFuncApprox)
        self.solver.set_integrator('dopri5', method = st.int_method, rtol=st.int_rtol, atol=st.int_atol)
        self.solver.set_initial_value(st.q0)
    
        self.x0 = st.q0        
        
    def stateFuncApprox(self, t, q):
      
        x1_o, x2_o, x3_o, x4_o = q
        y = self.sensor_output
        u = self.controller_output
#        print 'y: ',y
#        print 'u: ',u
#        print 'type(y): ',type(y)
#        print 'type(u): ',type(u)
        x_o = np.array([[x1_o],\
                      [x2_o],\
                      [x3_o],\
                      [x4_o]])
        #FIXME: sensorausgang mit C vermanschen
        # ACHTUNG!!!! y[0] überdenken für mehrgrößenfall
        y = np.dot(self.C, y.transpose())
        dx_o = np.dot(self.A - np.dot(self.L, self.C), x_o) + np.dot(self.B, u) + np.dot(self.L, y[0])
#        print 'dx_o: ',dx_o
        
        
        dx1_o = dx_o[0, 0]
        dx2_o = dx_o[1, 0]
        dx3_o = dx_o[2, 0]
        dx4_o = dx_o[3, 0]
        
        
        return [dx1_o, dx2_o, dx3_o, dx4_o]
        
    def estimate(self, t, controller_output=None, sensor_output=None):
        
        self.sensor_output = sensor_output
        self.controller_output = controller_output
        
        # sim_core Timer ist bereits einen Zeitschritt weiter
        observer_output = self.solver.integrate(t)           
        
        return observer_output
  
        