# -*- coding: utf-8 -*-

from __future__ import division
import sympy as sp

from numpy import sin, cos, pi
from scipy import special

from sim_core import SimulationModule

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
        yd.append(self.settings['Position'])
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        yd.append(0.)
        return yd

class TwoPointSwitchingTrajectory(Trajectory):
    '''
    provides a signal switching between two points
    '''

    settings = {'Positions': [0.5, -0.5],\
            'change time': 5,\
            }
    
    def __init__(self, derivateOrder):
        Trajectory.__init__(self, derivateOrder+1)
        self.switchCount = 1
        self.side = 0
    
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


class SmoothTransitionTrajectory(Trajectory):
    '''
    provides a trajektory from one state to the other
    '''

    settings = {'Positions': [0, 0.5],\
            'start time': 1,\
            'delta t': 3,\
            }
    
    def __init__(self, derivateOrder):
        Trajectory.__init__(self, derivateOrder+1)
        
        #setup symbolic expressions
        tau, k = sp.symbols('tau, k')

        gamma = derivateOrder
        alpha = sp.factorial(2*gamma+1)

        f = sp.binomial(gamma, k) * (-1)**k * tau**(gamma+k+1) / (gamma+k+1)
        phi = alpha/sp.factorial(gamma)**2 * sp.summation(f, (k, 0, gamma))

        #diff
        dphi_sym = [phi]
        for order in range(derivateOrder):
            dphi_sym.append(dphi_sym[-1].diff(tau))
        
        #lambdify
        self.dphi_num = []
        for der in dphi_sym:
            self.dphi_num.append(sp.lambdify(tau, der, 'numpy'))

    def calcValues(self, t):
        '''
        Calculates desired trajectory for ball position
        '''

        y = [0]*self.output_dim
        yd = self.settings['Positions']
        t0 = self.settings['start time']
        dt = self.settings['delta t']

        if t < t0:
            y[0] = yd[0]
        elif t > t0+dt:
            y[0] = yd[1]
        else:
            for order, dphi in enumerate(self.dphi_num):
                y[order] = yd[0] + (yd[1]-yd[0])*dphi((t-t0)/dt) * 1/dt**order

        return y
