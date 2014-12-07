# -*- coding: utf-8 -*-

from __future__ import division
from numpy import sin, cos, pi

from sim_core import SimulationModule

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
class Trajectory(SimulationModule):
    '''
    base class for trajectory generators
    '''

    def __init__(self, outputDimension):
        self.output_dim = outputDimension
        return

    def getOutputDimension(self):
        return self.output_dim

    def getValues(self, t):
        yd = self.calcValues(t)
        return [yd[i] for i in range(self.output_dim)]


class HarmonicTrajectory(Trajectory):
    ''' provide a harmonic signal with derivatives
    '''

    settings = {'Amplitude': 1.0}

    def __init__(self, derivateOrder):
        Trajectory.__init__(self, derivateOrder+1)
        if derivateOrder > 4:
            print 'Error: not enough derivates implemented!'

    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''
        yd = []
        A = float(self.settings['Amplitude'])
        yd.append(A * cos(pi*t/5))
        yd.append(-A * (pi/5) * sin(pi*t/5))
        yd.append(-A * (pi/5)**2 * cos(pi*t/5))
        yd.append(A * (pi/5)**3 * sin(pi*t/5))
        yd.append(A * (pi/5)**4 * cos(pi*t/5))
        return yd

class FixedPointTrajectory(Trajectory):
    ''' provides a fixed signal
    '''
    
    settings = {'Position': 1.0}
    
    def __init__(self, derivateOrder):
        Trajectory.__init__(self, derivateOrder+1)
    
    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''
        yd = []
        yd.append(float(self.settings['Position']))
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        return yd

#TODO: Anfahren verschiedener Positionen
