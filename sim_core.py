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

    def __init__(self, model, initialState=None, trajectory=None, sensor=None, controller=None, logger=None):
        # model
        self.model = model
        self.model_output = 0

        # solver
        self.solver = ode(model.stateFunc)
        if initialState is not None:
            q = initialState
        else:
            q = q0

        self.solver.set_initial_value(q)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)

        #sensor
        self.sensor = sensor
        self.sensor_output = 0
       
        #trajectory
        self.trajectory = trajectory
        self.traj_output = 0

        #controller
        self.controller = controller
        if controller is not None:
            self.tOrder = controller.getOrder()
        else:
            self.tOrder = 0

        self.controller_output = 0
        
        #Logging
        self.logger = logger

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        
        # integrate model
        self.model.setInput(self.controller_output)
        s = self.solver
        self.model_output = s.integrate(s.t+dt) 

        #perform measurement
        if self.sensor is not None:
            self.sensor_output = self.sensor.measure(s.t, self.model_output)
        else:
            self.sensor_output = self.model_output

        #get desired values
        if self.trajectory is not None:
            self.traj_output = self.trajectory.getValues(s.t, self.tOrder)
        else:
            self.traj_output = 0

        #perform control
        if self.controller is not None:
            self.controller_output = self.controller.control(self.sensor_output, self.traj_output)
        else:
            self.controller_output = 0

        #store
        if self.logger is not None:
            data = {'t':s.t}
            for i in range(self.model.getStates()):
                data.update({('x%i' % (i+1)): self.model_output[i]})

            self.logger.log(data)

        return self.model_output

