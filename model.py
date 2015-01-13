#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

#from numpy import sin, cos, pi
#from numpy import array as narray
import numpy as np

from sim_core import SimulationModule
import settings as st

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

    settings = {'M': st.M,  \
            'R': st.R,      \
            'J': st.J,      \
            'Jb': st.Jb,     \
            'G': st.G,      \
            'beam length': st.beam_length,      \
            'beam width': st.beam_width,      \
            'beam depth': st.beam_depth,      \
            }

    def __init__(self):
        SimulationModule.__init__(self)
        self.states = 4
        self.firstRun = True

    def stateFunc(self, t, q, tau=0):
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
        dx2 = self.B*(x1*x4**2 - self.G*np.sin(x3))
        dx3 = x4

        #inverse nonliniear system transformation
        u = (tau - self.M* (2*x1*x2*x4 + self.G*x1*np.cos(x3))) / (self.M*x1**2 + self.J + self.Jb)
        dx4 = u
       
        return [dx1, dx2, dx3, dx4]

    def checkConsistancy(self, state):
        ''' Checks if the model rules are violated
        '''
        if abs(state[0]) > float(self.settings['beam length'])/2:
            raise ModelException('Ball fell down.')
        if abs(state[2]) > np.pi/2:
            raise ModelException('Beam reached critical angle.')

    def calcPositions(self, q):
        '''
        Calculate stationary vectors and rot. matrices for bodies
        '''
        #beam
        T_beam = np.array([[np.cos(q[2]), -np.sin(q[2]), 0],\
                            [np.sin(q[2]), np.cos(q[2]), 0],\
                            [0, 0, 1]])
        r_beam0 = np.array([0, -st.visR - st.visBeamWidth/2, 0])
        r_beam = np.dot(T_beam, r_beam0)

        #ball
        r_ball0 = np.array([q[0], 0, 0])
        r_ball = np.dot(T_beam, r_ball0)
        phi = q[0]/st.visR
        T_ball = np.array([[np.cos(phi), -np.sin(phi), 0],\
                            [np.sin(phi), np.cos(phi), 0],\
                            [0, 0, 1]])

        return r_beam, T_beam, r_ball, T_ball
