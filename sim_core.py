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

    traj_gen = None
    controller = None
    model = None
    solver = None
    logger = None
    visualizer = None

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



    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        s = self.solver
        data = {'t' : s.t, 'q' : s.integrate(s.t+dt) }

        return data

