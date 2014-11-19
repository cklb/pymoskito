#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos, array

from settings import *
from logging import GraphLogger

import numpy as np


#---------------------------------------------------------------------
# controller base class 
#---------------------------------------------------------------------
class Controller:

    trajGen = None
    order = 0

    def __init__(self, trajGen):
        self.trajGen = trajGen
        return

    def control(self, t, x):
        yd = self.trajGen.getValues(t, self.order)

        return self.calcOutput(x, yd)

#---------------------------------------------------------------------
# P controller
#---------------------------------------------------------------------
class PController(Controller):
    '''
    PController with a negative controller gain
    - with reference to bode diagram --> negative gain
    - system is unstable, because the controller is too slow
    - e.g. inital states x = [0, 0.2, 0, 0], desired position r = 0
    '''
    
    # controller fails, because he is stupid   
    # controller gain
    Kp = -0.6
    
    def __init__(self, trajGen):
        self.order = 0
        Controller.__init__(self, trajGen)
        
    def calcOutput(self, x, yd):
        
        u = self.Kp*(yd[0]-x[0])
        
        
        return u


#---------------------------------------------------------------------
# controller created by changing f(x) 
#---------------------------------------------------------------------
class FController(Controller):

    # controller gains
    k0 = 16
    k1 = 32
    k2 = 24
    k3 = 8
    

    def __init__(self, trajGen):
        self.order = 4
        Controller.__init__(self, trajGen)
        self.log = GraphLogger(name='u', yonly=True)

    def calcOutput(self, x, yd):
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*sin(x[2])
        phi4 = -B*G*x[3]*cos(x[2])
        
        # calculate fictional input v
        v = yd[4] + \
                self.k3*(yd[3] - phi4) + \
                self.k2*(yd[2] - phi3) + \
                self.k1*(yd[1] - phi2) + \
                self.k0*(yd[0] - phi1)
        
        # calculate a(x)
        a = -B*G*cos(x[2])
        # calculate b(x)
        b = B*G*x[3]**2*sin(x[2])
        
        # calculate u
        u = (v-b)/a
        self.log.log(None, [u])
        
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
    
    def __init__(self, trajGen):
        self.order = 4
        Controller.__init__(self, trajGen)
        
    def calcOutput(self, x, yd):
        
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*sin(x[2]) + B*x[0]*x[3]**2
        phi4 = -B*G*x[3]*cos(x[2]) + B*x[1]*x[3]**2
        
        # calculate fictional input v
        v = yd[4] + \
                self.k3*(yd[3] - phi4) + \
                self.k2*(yd[2] - phi3) + \
                self.k1*(yd[1] - phi2) + \
                self.k0*(yd[0] - phi1)
        
        # calculate a(x)
        a = -B*G*cos(x[2]) + 2*B*x[1]*x[3]
        # calculate b(x)
        b = B**2+x[0]*x[3]**4 + B*G*(1 - B)*x[3]**2*sin(x[2])
        
        # calculate u
        u = (v-b)/a
        
        return u

#---------------------------------------------------------------------
# controller based on the standard jacobian approximation
#---------------------------------------------------------------------

class JController(Controller):
    
    # controller gains
    k0 = 16
    k1 = 32
    k2 = 24
    k3 = 8
    
    def __init__(self, trajGen):
        self.order = 4
        Controller.__init__(self, trajGen)
    
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
    
    # Zustandsrückführung mit Eigenwerte bei -2
    K = array([-0.5362, -0.0913, 0.48, 0.16])

    # Vorfilter V = -[C(A-BK)^-1*B]^-1
    V = -0.0457
    
    def __init__(self, trajGen):
        self.order = 0
        Controller.__init__(self, trajGen)
        
    def calcOutput(self, x, yd):
        
        # calculate u
        u = np.dot(-self.K,np.transpose(x)) + yd[0]*self.V
        
        return u
        
#print 'x1=%f , x2=%f, x3=%f, x4=%f, u=%f, yd=%f' % (x[0],x[1],x[2],x[3],u,yd[0])
