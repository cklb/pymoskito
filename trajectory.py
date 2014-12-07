#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import sin, cos, pi
import settings as sp

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
    ''' 
    provide a harmonic signal with derivatives
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
    ''' 
    provides a fixed signal
    '''
    
    pos = 0
    
    def __init__(self, logger=None):
        TrajectoryGenerator.__init__(self, logger)
    
    def setPosition(self, position):
        if abs(position) <= sp.beam_length/2:
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

class TwoPointSwitchingGenerator(TrajectoryGenerator):
    '''
    provides a signal which switched between two different points
    '''
    pos1 = sp.beam_length/2
    pos2 = -sp.beam_length/2
    counter = 1
    change = 5
    changeTime = sp.sim_time/change
    
    def __init__(self, logger=None):
        TrajectoryGenerator.__init__(self, logger)
    
    def setPositions(self, position1, position2):
        '''
        set the position1 and position2
        '''
        if (abs(position1) <= sp.beam_length/2) and (abs(position2) <= sp.beam_length/2):
                self.pos1 = position1
                self.pos2 = position2
        else:
                print 'One of the positions is not on the beam, it is set to r = 0.5 and r = -0.5'
                self.pos1 = sp.beam_length/2
                self.pos2 = -sp.beam_length/2
                
    def setNumberOfChange(self, change):
        '''
        Set the number of change between two points
        '''
        self.change = change
        self.changeTime = sp.sim_time/change
        
            
    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''
        yd = []
        
        if t < self.changeTime*self.counter:
            yd.append(self.pos1)
        else:
            yd.append(self.pos2)
            if t > self.changeTime*(self.counter + 1):
                self.counter = self.counter + 2
        
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
    
        return yd
