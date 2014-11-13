#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import division
from scipy.integrate import ode

from settings import *
from logging import GraphLogger

#--------------------------------------------------------------------- 
# Core of the physical simulation
#--------------------------------------------------------------------- 
class Simulator:
    """ Simulation Wrapper
    
    This Class exceutes the timestep integration.
    """

    model = None
    solver = None
    logger = None

    def __init__(self, model, initialState=None):
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
        self.logger = GraphLogger(name='System States', dimensions = 4)

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        s = self.solver
        data = [s.t, s.integrate(s.t+dt)]

        if self.logger is not None:
            self.logger.log(data[0], data[1])

        return data

