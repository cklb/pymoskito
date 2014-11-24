#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos, pi
from settings import *

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
class TrajectoryGenerator:
    '''
    base class for trajectory generators
    '''

    def __init__(self, logger=None):
        self.logger = logger

    def getValues(self, t, order):
        yd = self.calcValues(t)
        return [yd[i] for i in range(order+1)]

class HarmonicGenerator(TrajectoryGenerator):
    ''' provide a harmonic signal with derivatives
    '''

    def __init__(self, logger=None):
        TrajectoryGenerator.__init__(self, logger)
        self.A = 1

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

class FixedPointGenerator(TrajectoryGenerator):
    ''' provides a fixed signal
    '''
    
    pos = 0
    
    def __init__(self, logger=None):
        TrajectoryGenerator.__init__(self, logger)
    
    def setPosition(self, position):
        if abs(position) <= beam_length/2:
            self.pos = position
        else:
            print 'This position is not on the beam, it is set to r = 0'
            self.pos = 0
    
    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''
        yd = []
        yd.append(self.pos)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)

        return yd

#TODO: Anfahren verschiedener Positionen
