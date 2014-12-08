# -*- coding: utf-8 -*-

import numpy as np
from sim_core import SimulationModule

#---------------------------------------------------------------------
# Disturbance base class 
#---------------------------------------------------------------------
class Disturbance(SimulationModule):

    def __init__(self, outputDimension):
        SimulationModule.__init__(self)
        self.output_dim = outputDimension
        return

    def getOutputDimension(self):
        return self.output_dim

    def disturb(self, t):
        z = self.calcOutput(t)
        return z

#---------------------------------------------------------------------
# Gaussion Noise
#---------------------------------------------------------------------
class GaussionNoiseDisturbance(Disturbance):
    ''' Gaussion Noise
        
    '''
    settings = {'mean value': 0,\
                'sigma': .1, \
                }

    def __init__(self, outputDimension):
        SimulationModule.__init__(self)
        Disturbance.__init__(self, outputDimension)

    def calcOutput(self, t):
        return np.random.normal(self.settings['mean value'], \
                self.settings['sigma'], self.output_dim)
