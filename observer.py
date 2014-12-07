# -*- coding: utf-8 -*-

import numpy as np
from sim_core import SimulationModule

#---------------------------------------------------------------------
# obeserver base class 
#---------------------------------------------------------------------
class Observer(SimulationModule):

    def __init__(self):
        SimulationModule.__init__(self)
        return

    def getOutputDimension(self):
        return self.output_dim

    def obeserve(self, u):
        u = self.calcOutput(u)
        return u

#---------------------------------------------------------------------
# Luenberger Observer
#---------------------------------------------------------------------
class LuenbergerObserver(Observer):
    '''
    Luenberger Observer
    '''

    settings = {}
    
    def __init__(self):
        self.output_dim = 4 #oberver complete state
        Observer.__init__(self)
        
    def calcOutput(self, u):
        y = [0, 0, 0, 0] #TODO
        return y

