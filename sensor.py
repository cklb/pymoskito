#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from sim_core import SimulationModule

#---------------------------------------------------------------------
# sensor base class 
#---------------------------------------------------------------------
class Sensor(SimulationModule):


    def __init__(self):
        ''' initialize the sensor
        '''
        SimulationModule.__init__(self)

    def measure(self, time, y):
        u = self.calcOutput(time, y)
        return [u[int(x)] for x in self.settings['output']]

    def getOutputDimension(self):
        return len(self.settings['output'])

class DeadTimeSensor(Sensor):

    settings = {'output': '[0,1,2,3]', \
                'delay': 1,\
                }

    def __init__(self, inputDimension):
        Sensor.__init__(self)
        self.inputDimension = inputDimension
        self.firtRun = True
        
    def calcOutput(self, t, y):
        if self.firtRun == True:
            self.storage = [[0.0 for i in range(self.inputDimension)] for x in range(int(self.settings['delay']))]
            self.firtRun = False
        self.storage.append(y)
        return self.storage.pop(0)

