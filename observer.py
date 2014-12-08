# -*- coding: utf-8 -*-
import numpy as np
from scipy.integrate import ode

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

    settings = {'Method': 'adams',\
            'step size': 0.01,\
            'rTol': 1e-6,\
            'aTol': 1e-9,\
            'end time': 10,\
            'initial state': [0, 0, 0, 0],\
            'poles': [-3, -3, -3, -3],\
            }

    def __init__(self, linearization):
        self.output_dim = 4 #oberver complete state
        Observer.__init__(self)
        self.firstRun = True
              
    def stateFuncApprox(self, t, q):
        if self.firstRun:
            self.A = linearization.A
            self.B = linearization.B
            self.C = linearization.C
            self.L = linearization.calcObserver(self.settings['poles'])
            
            self.solver = ode(self.stateFuncApprox)
            self.solver.set_integrator('dopri5', method=self.settings['method'], \
                    rtol=self.settings['rTol',\
                    atol=self.settings['aTol')
            self.solver.set_initial_value(self.settings['initial state'])
        
            self.x0 = self.settings['initial state']     
            self.firstRun = False
      
        x1_o, x2_o, x3_o, x4_o = q
        y = self.sensor_output
        u = self.controller_output
#        print 'y: ',y
#        print 'u: ',u
#        print 'type(y): ',type(y)
#        print 'type(u): ',type(u)
        x_o = np.array([[x1_o],\
                      [x2_o],\
                      [x3_o],\
                      [x4_o]])
        #FIXME: sensorausgang mit C vermanschen
        # ACHTUNG!!!! y[0] überdenken für mehrgrößenfall
        y = np.dot(self.C, y.transpose())
        dx_o = np.dot(self.A - np.dot(self.L, self.C), x_o) + np.dot(self.B, u) + np.dot(self.L, y[0])
#        print 'dx_o: ',dx_o
        
        
        dx1_o = dx_o[0, 0]
        dx2_o = dx_o[1, 0]
        dx3_o = dx_o[2, 0]
        dx4_o = dx_o[3, 0]
        
        
        return [dx1_o, dx2_o, dx3_o, dx4_o]
        
    def calcOutput(self, t, controller_output=None, sensor_output):
        self.sensor_output = sensor_output
        self.controller_output = controller_output
        
        # sim_core Timer ist bereits einen Zeitschritt weiter
        observer_output = self.solver.integrate(t)           
        
        return observer_output

