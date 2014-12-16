# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 13:09:58 2014

@author: Topher
"""

import sympy as sp
import numpy as np
from sim_core import SimulationModule
import settings as st

class Feedforward(SimulationModule):

    def __init__(self, order):
        SimulationModule.__init__(self)
        self.order = order
        return

    def getOrder(self):
        return self.order

    def getOutputDimension(self):
        return 1

    def feed(self, yd):
        u = self.calcOutput(yd)
        return u

class ApproximateFeedforward(Feedforward):
    
    settings = {'M': st.M,  \
        'R': st.R,      \
        'J': st.J,      \
        'Jb': st.Jb,     \
        'G': st.G,      \
        'beam length': st.beam_length,      \
        'beam width': st.beam_width,      \
        'beam depth': st.beam_depth,      \
        }


    derOrder = 2
    
    def __init__(self):
        Feedforward.__init__(self, 2+self.derOrder)
        self.theta_t = lambda rdd: -1/(self.settings['M']*self.settings['G']) \
                            *(self.settings['Jb']/self.settings['R']**2 \
                                + self.settings['M']) * rdd
    def calcOutput(self, yd):
        tau = 0
        
        theta = []
        for i in range(self.derOrder+1):
            theta.append(self.theta_t(yd[i+2]))
        
        tau = (self.settings['J']+self.settings['Jb'])*theta[2] \
                + self.settings['M']*self.settings['G']*yd[0]

        return tau
        
class TighterApproximateFeedforward(Feedforward):
    '''
    Calculation of tau is more precise than in the ApproximateFeedforward
    '''
    
    settings = {'M': st.M,  \
        'R': st.R,      \
        'J': st.J,      \
        'Jb': st.Jb,     \
        'G': st.G,      \
        'beam length': st.beam_length,      \
        'beam width': st.beam_width,      \
        'beam depth': st.beam_depth,      \
        }
        
    derOrder = 2
    
    def __init__(self):
        Feedforward.__init__(self, 2 + self.derOrder)
        self.theta_t = lambda rdd: -1/(self.settings['M']*self.settings['G']) \
                                *(self.settings['Jb']/self.settings['R']**2 \
                                + self.settings['M']) * rdd
    def calcOutput(self, yd):
        tau = 0
        theta = []
        for i in range(self.derOrder + 1):
            theta.append(self.theta_t(yd[i+2]))
        
        tau = (self.settings['M']*yd[2]**2 + self.settings['J'] \
                + self.settings['Jb'])*theta[2] \
                + 2*self.settings['M']*yd[0]*yd[1]*theta[1] \
                + self.settings['M']*self.settings['G']*yd[0]*np.cos(theta[0])
                

        return float(tau)
        
        
        
        
        
        
        
        
        
        
        
        
        
        