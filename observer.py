# -*- coding: utf-8 -*-
import numpy as np
from scipy.integrate import ode

from sim_core import SimulationModule
from linearization import Linearization

#---------------------------------------------------------------------
# obeserver base class 
#---------------------------------------------------------------------
class Observer(SimulationModule):

    def __init__(self):
        SimulationModule.__init__(self)
        return

    def getOutputDimension(self):
        return self.output_dim

    def observe(self, t, u, r):
        y = self.calcOutput(t, u, r)
        return y

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
            'lin state': [0, 0, 0, 0],\
            'lin tau': 0,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True
              
    def stateFuncApprox(self, t, q):
        x1_o, x2_o, x3_o, x4_o = q
        y = np.array(self.sensor_output)
        u = self.controller_output

        x_o = np.array([[x1_o],\
                      [x2_o],\
                      [x3_o],\
                      [x4_o]])
        #FIXME: sensorausgang mit C vermanschen
        # ACHTUNG!!!! y[0] überdenken für mehrgrößenfall
        #y = np.dot(self.C, y.transpose())
        dx_o = np.dot(self.A - np.dot(self.L, self.C), x_o) + np.dot(self.B, u) + np.dot(self.L, y[0])
        
        dx1_o = dx_o[0, 0]
        dx2_o = dx_o[1, 0]
        dx3_o = dx_o[2, 0]
        dx4_o = dx_o[3, 0]
        
        
        return [dx1_o, dx2_o, dx3_o, dx4_o]
        
    def calcOutput(self, t, controller_output, sensor_output):
        if self.firstRun:
            self.lin = Linearization(self.settings['lin state'], self.settings['lin tau'])

            self.A = self.lin.A
            self.B = self.lin.B
            self.C = self.lin.C
            L_T = self.lin.ackerSISO(self.lin.A.transpose(),self.lin.C.transpose(),self.settings['poles'])
            self.L = L_T.transpose()
            
            self.solver = ode(self.stateFuncApprox)
            self.solver.set_integrator('dopri5', method=self.settings['Method'], \
                    rtol=self.settings['rTol'],\
                    atol=self.settings['aTol'])
            self.solver.set_initial_value(self.settings['initial state'])
        
            self.x0 = self.settings['initial state']     
            self.firstRun = False


        self.sensor_output = sensor_output
        self.controller_output = controller_output
        
        # sim_core Timer ist bereits einen Zeitschritt weiter
        observer_output = self.solver.integrate(t)           
        
        return observer_output

