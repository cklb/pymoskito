#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from simulation_modules import SimulationModule

#---------------------------------------------------------------------
# limiter base class 
#---------------------------------------------------------------------
class Limiter(SimulationModule):

    def __init__(self):
        ''' initialize the limiter
        '''
        SimulationModule.__init__(self)

    def limit(self, input):
        u = self.calcOutput(input)
        return u

    def getOutputDimension(self):
        return 1

class AmplitudeLimiter(Limiter):

    settings = {'limits': '[-2, 2]', \
                }

    def __init__(self):
        Limiter.__init__(self)
        
    def calcOutput(self, r):
        out = min(self.settings['limits'][1],\
                max(r, self.settings['limits'][0]))
        return out
        
