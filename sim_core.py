#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import division
from scipy.integrate import ode

from settings import *

#--------------------------------------------------------------------- 
# Core of the physical simulation
#--------------------------------------------------------------------- 
class Simulator:
    """ Simulation Wrapper
    
    This Class exceutes the timestep integration.
    """

    model = None
    solver = None

    def __init__(self, model, initialState=None, logger=None):
        # model
        self.model = model

        # solver
        self.solver = ode(model.stateFunc)
        if initialState is not None:
            q = initialState
        else:
            q = q0

        self.solver.set_initial_value(q)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)
        #Logging
        self.logger = logger

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''

        s = self.solver
        t, self.model_output = s.integrate(s.t+dt) 
        self.model_input = self.controller.control(self.model_output)

        if self.logger is not None:
            data = {'t':s.t}
            for i in range(model.states):
                data.update(('x%' % (i+1)), self.model_output[i])

            self.logger.log(data)

        return t, x

