#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos

from settings import *

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

    def calcOutput(self, x, yd):
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -B*G*sin(x[2])
        phi4 = -B*G*x[3]*sin(x[2])
        
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
        
        return u

