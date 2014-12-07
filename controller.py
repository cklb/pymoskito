#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

from settings import *
import linearization as lin
from sim_core import SimulationModule

#---------------------------------------------------------------------
# controller base class 
#---------------------------------------------------------------------
class Controller(SimulationModule):

    order = 0

    def __init__(self):
        SimulationModule.__init__(self)
        return

    def getOrder(self):
        return self.order

    def getOutputDimension(self):
        #no extra necessary all the same
        return 1

    def control(self, x, w):
        u = self.calcOutput(x, w)
        return u

#---------------------------------------------------------------------
# P controller
#---------------------------------------------------------------------
class PController(Controller):
    '''
    PController
    - e.g. inital states x = [0, 0.2, 0, 0], desired position r = 0
    '''
    
    # controller gain
    Kp = -0.6
    
    def __init__(self):
        self.order = 0
        Controller.__init__(self)
        
    def calcOutput(self, x, w):
        u = self.Kp*(w[0]-x[0])
        return u

#---------------------------------------------------------------------
# controller created by changing f(x) 
#---------------------------------------------------------------------
class FController(Controller):

    # controller gains
    k0 = 16.
    k1 = 32.
    k2 = 24.
    k3 = 8.

    def __init__(self):
        self.order = 4
        Controller.__init__(self)

    def calcOutput(self, x, yd):
        
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*np.sin(x[2])
        phi4 = -B*G*x[3]*np.cos(x[2])
        
        # calculate fictional input v
        v = yd[4] + \
                self.k3*(yd[3] - phi4) + \
                self.k2*(yd[2] - phi3) + \
                self.k1*(yd[1] - phi2) + \
                self.k0*(yd[0] - phi1)
        
        # calculate a(x)
        a = -B*G*np.cos(x[2])
        # calculate b(x)
        b = B*G*x[3]**2*np.sin(x[2])
        
        # calculate u
        u = (v-b)/a
        
        #print phi1, phi2, phi3, phi4
        #print a, b, v, u
        return u

#---------------------------------------------------------------------
# controller created by changing g(x) 
#---------------------------------------------------------------------
class GController(Controller):
    
    # controller gains
    k0 = 16
    k1 = 32
    k2 = 24
    k3 = 8
    
    def __init__(self):
        self.order = 4
        Controller.__init__(self)
        
    def calcOutput(self, x, yd):
        
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*np.sin(x[2]) + B*x[0]*x[3]**2
        phi4 = -B*G*x[3]*np.cos(x[2]) + B*x[1]*x[3]**2
        
        # calculate fictional input v
        v = yd[4] + \
                self.k3*(yd[3] - phi4) + \
                self.k2*(yd[2] - phi3) + \
                self.k1*(yd[1] - phi2) + \
                self.k0*(yd[0] - phi1)
        
        # calculate a(x)
        a = -B*G*np.cos(x[2]) + 2*B*x[1]*x[3]
        # calculate b(x)
        b = B**2+x[0]*x[3]**4 + B*G*(1 - B)*x[3]**2*np.sin(x[2])
        
        # calculate u
        u = (v-b)/a
        
        return u

#---------------------------------------------------------------------
# controller based on the standard jacobian approximation
#---------------------------------------------------------------------
class JController(Controller):
    
    # controller gains
    k0 = 16.0
    k1 = 32.0
    k2 = 24.0
    k3 = 8.0
    
    def __init__(self):
        self.order = 4
        Controller.__init__(self)
    
    def calcOutput(self, x, yd):
        
        # calculate linear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*x[2]
        phi4 = -B*G*x[3]
        
        # calculate fictional input v
        v = yd[4] + \
                self.k3*(yd[3] - phi4) + \
                self.k2*(yd[2] - phi3) + \
                self.k1*(yd[1] - phi2) + \
                self.k0*(yd[0] - phi1)
        
        # calculate a(x)
        a = -B*G/(J + Jb)
        # calculate b(x)
        b = B*M*G**2*x[0]/(J + Jb)
        
        # calculate u
        u = (v-b)/a
        
        return u

#---------------------------------------------------------------------
# linear statespace controller
#---------------------------------------------------------------------
class LSSController(Controller):
    '''
    linear statespace controller
    System is linearised by tau = 0 and x = [0,0,0,0]
    '''
    # Zustandsrückführung mit Eigenwerten bei -2
#    K = np.array([-0.5362, -0.0913, 0.48, 0.16])
#    V = -0.0457
    
    def __init__(self):
        Controller.__init__(self)
    
        l = lin.Linearization(x0=[0.5,0,0,0],tau0=0)
        self.K = l.polesToAckermann([-2,-2,-2,-2])
        self.V = l.prefilter(self.K)
        self.order = 0
        
    def calcOutput(self, x, yd):
        # calculate u
        u = np.dot(-self.K,np.transpose(x)) + yd[0]*self.V
        
        return u[0]
        
#---------------------------------------------------------------------
# Input-Output-Linearization
#---------------------------------------------------------------------
class IOLController(Controller):
    '''
    Input-Output-Linearisation-Controller with managed non well defined 
    relative degree
    - this controller fails!!!
    '''
    # controller gains
    k0 = 8
    k1 = 12
    k2 = 6
    
    def __init__(self):
        self.order = 3
        Controller.__init__(self)
        
    def calcOutput(self, x, yd):
        print 'x:',x
        print 'yd:',yd

        # calculate y terms
        y = x[0]
        y_d = x[1]
        y_dd = B*x[0]*x[3]**2 -B*G*np.sin(x[2]) 
        
        # calculate fictional input v
        v = yd[3] + \
                self.k2*(yd[2] - y_dd) + \
                self.k1*(yd[1] - y_d) + \
                self.k0*(yd[0] - y)
        
        # calculate a(x)
        a = 2*B*x[0]*x[3]
        # calculate b(x)
        b = B*x[1]*x[3]**2 - B*G*x[3]*np.cos(x[2])
        
        # calculate u
        if np.absolute(a) < 0.3:     
            u = 0
        else:
            u = (v-b)/a

        print 'u', u
        return u
    
        #print 'x1=%f , x2=%f, x3=%f, x4=%f, u=%f, yd=%f' % (x[0],x[1],x[2],x[3],u,yd[0])

