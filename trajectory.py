# -*- coding: utf-8 -*-

from __future__ import division
from numpy import sin, cos, pi
<<<<<<< HEAD
import settings as sp
=======

from sim_core import SimulationModule
>>>>>>> model_view_architecture

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
class Trajectory(SimulationModule):
    '''
    base class for trajectory generators
    '''

    def __init__(self, outputDimension):
        SimulationModule.__init__(self)
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

    settings = {'Amplitude': 0.5}

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
    
    settings = {'Position': 0.5}
    
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

class TwoPointSwitchingTrajectoy(TrajectoryGenerator):
    '''
    provides a signal switching between two points
    '''

    settings = {'Positions': [0.5, -0.5],\
            'change time': 5} #keine Ahnung was das ist
    
    def __init__(self, derivateOrder):
        Trajectory.__init__(self, derivateOrder+1)
        self.switchCount = 1
    
    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''

        yd = []
        if t > self.settings['change time']*self.switchCount:
            #time to switch
            if self.side == 0:
                self.side = 1
            else:
                self.side = 0
            self.switchCount += 1
        
        yd.append(self.settings['Positions'][self.side])
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
    
        return yd
