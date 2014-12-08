#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos, pi
from numpy import array as narray

from sim_core import SimulationModule

#---------------------------------------------------------------------
# implementation of the system in state space form
#--------------------------------------------------------------------- 
class ModelException(Exception):
    pass

class SimulationModel(SimulationModule):

    def __init__(self):
        SimulationModule.__init__(self)

    def getOutputDimension(self):
        return self.states

class BallBeamModel(SimulationModel):

    settings = {'M': 0.05,  \
            'R': 0.01,      \
            'J': 0.02,      \
            'Jb': 2e-6,     \
            'G': 9.81,      \
            'beam length': 2.0,      \
            'beam width': 0.01,      \
            'beam depth': 0.03,      \
            }

    def __init__(self):
        SimulationModule.__init__(self)
        self.tau = 0
        self.states = 4
        self.firstRun = True

    def setInput(self, model_input):
        self.tau = model_input

    def stateFunc(self, t, q):
        '''
        Calculations of system state changes
        '''
        if self.firstRun:
            #abbreviations
            self.M = self.settings['M']
            self.R = self.settings['R']
            self.J = self.settings['J']
            self.Jb = self.settings['Jb']
            self.G = self.settings['G']
            self.B = self.M/(self.Jb/self.R**2+self.M)
            self.firstRun = False

        #definitoric
        x1 = q[0]
        x2 = q[1]
        x3 = q[2]
        x4 = q[3]
        y = x1

        dx1 = x2
        dx2 = self.B*(x1*x4**2 - self.G*sin(x3))
        dx3 = x4

        #inverse nonliniear system transformation
        u = (self.tau - self.M* (2*x1*x2*x4 + self.G*x1*cos(x3))) / (self.M*x1**2 + self.J + self.Jb)
        dx4 = u
       
        return [dx1, dx2, dx3, dx4]

    def checkConsistancy(self, state):
        ''' Checks if the model rules are violated
        '''
        if abs(state[0]) > float(self.settings['beam length'])/2:
            raise ModelException('Ball fell down.')
        if abs(state[2]) > pi/2:
            raise ModelException('Beam reached critical angle.')

    def calcPositions(self, q):
        '''
        Calculate stationary vectors and rot. matrices for bodies
        '''
        #beam
        r_beam = [0, -self.settings['R']/2 - self.settings['beam width'], 0]
        T_beam = narray([[cos(q[2]), -sin(q[2]), 0], [sin(q[2]), cos(q[2]), 0], [0, 0, 1]])

        #ball
        r_ball = [cos(q[2])*q[0], sin(q[2])*q[0], 0]
        T_ball = narray([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        return r_beam, T_beam, r_ball, T_ball
