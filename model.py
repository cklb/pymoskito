#!/usr/bin/python
# -*- coding: utf-8 -*-

from settings import *
from numpy import sin, cos, pi

#---------------------------------------------------------------------
# implementation of the system in state space form
#--------------------------------------------------------------------- 

class BallBeamModel:

    def __init__(self, controller):
        self.controller = controller

    def stateFunc(self, t, q):
        '''
        Calculations of system state changes
        '''
        #definitoric
        x1 = q[0]
        x2 = q[1]
        x3 = q[2]
        x4 = q[3]
        y= x1

        dx1 = x2
        dx2 = B*(x1*x4**2 - G*sin(x3))
        dx3 = x4

        #call controller
        tau = self.controller.control(t, q)

        #inverse nonliniear system transformation
        u = (tau - M* (2*x1*x2*x4 + G*x1*cos(x3))) / (M*x1**2 + J + Jb)
        dx4 = u

        return [dx1, dx2, dx3, dx4]

    def calcPositions(q):
        '''
        Calculate stationary vectors and rot. matrices for bodies
        '''

        #beam
        r_beam = [0, -R/2 - beam_width, 0]
        T_beam = narray([[cos(q[2]), -sin(q[2]), 0], [sin(q[2]), cos(q[2]), 0], [0, 0, 1]])

        #ball
        r_ball = [cos(q[2])*q[0], sin(q[2])*q[0], 0]
        T_ball = narray([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        return r_beam, T_beam, r_ball, T_ball
