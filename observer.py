# -*- coding: utf-8 -*-
"""
Created on Tue Dec 02 21:47:52 2014

@author: cle
"""

import sympy as sp
import numpy as np

from scipy.integrate import ode
from settings import *

class LuenbergerObserver:
    
    x0 = q0
    
    def __init__(self, A=None, B=None, C=None, K=None, L=None):
        self.A = A
        self.B = B
        self.C = C
        self.L = L
        self.K = K
        
    def stateFncApprox(self, t, q):
        A = self.A
        B = self.B
        C = self.C
        L = self.L
        K = self.K                  
        
        #FIXME: welches u nehmen, nehme einfach u=-k * x_dach
        x1s, x2s, x3s, x4s = q
        y = self.sensor_output
        
        xs = np.array([[x1s],\
                      [x2s],\
                      [x3s],\
                      [x4s]])        
        
        dxs = np.dot(A - np.dot(B,K) - np.dot(L, C), xs) + np.dot(L, self.y)
        
        dx1s = dxs[0, 0]
        dx2s = dxs[1, 0]
        dx3s = dxs[2, 0]
        dx4s = dxs[3, 0]
        
        
        return [dx1s, dx2s, dx3s, dx4s]
        
    def estimate(self, sensor_output=None):
        
#        self.sensor_output = sensor_output
#        
#        
#        x0 = self.x0
#        
#        solver = ode(self.stateFncApprox)
#        solver.set_initial_value(x0)
#        
#        int_mode = 'vode'
#        int_method='adams'
#        int_rtol=1e-6
#        int_atol=1e-9
#        solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)
#        
#        
#        tend = dt
#        dtObserv = dt / 10.0
#        a1 = []
#        a2 = []
#        while solver.successful() and solver.t < tend:
#            solver.integrate(solver.t+dtObserv)
##            print ("%g %g" % (solver.t, solver.y))
#            a1.append(solver.t)
#            a2.append(solver.y)
#            

#        xs = solver.y[-1]
#            
#        #FIXME: wirklcih so???
#            
#        self.x0 = [xs[0], xs[1], xs[2], xs[3]]
#        
#        return [xs[0], xs[1], xs[2], xs[3]]
        return sensor_output
  
        