#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos, pi

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
class TrajectoryGenerator:
    '''
    base class for trajectory generators
    '''

    def __init__(self):
        pass

    def getValues(self, t, order):
        yd = self.calcValues(t)
        return [yd[i] for i in range(order+1)]

class HarmonicGenerator(TrajectoryGenerator):

    A = 0

    def __init__(self):
        TrajectoryGenerator.__init__(self)

    def setAmplitude(self, Amplitude):
        self.A = Amplitude

    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''
        yd = []
        yd.append(self.A * cos(pi*t/5))
        yd.append(-self.A * (pi/5) * sin(pi*t/5))
        yd.append(-self.A * (pi/5)**2 * cos(pi*t/5))
        yd.append(self.A * (pi/5)**3 * sin(pi*t/5))
        yd.append(self.A * (pi/5)**4 * cos(pi*t/5))

        return yd
            
