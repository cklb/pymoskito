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

        # solver
        self.solver = ode(model.stateFunc)
        if initialState is not None:
            self.q = initialState
        else:
            self.q = q0

        self.solver.set_initial_value(self.q)
        self.solver.set_integrator(int_mode, method=int_method, rtol=int_rtol, atol=int_atol)

        #sensor
        self.sensor = sensor
       
        #trajectory
        self.trajectory = trajectory

        #controller
        self.controller = controller
        if controller is not None:
            self.tOrder = controller.getOrder()
        else:
            self.tOrder = 0

        self.controller_output = 0
        
        #Logging
        self.logger = logger
        
        #erster Durchlauf
        self.start = True

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        
        # integrate model
        self.model.setInput(self.controller_output)
        s = self.solver
        model_output = s.integrate(s.t+dt) 

        #check credibility
        self.model.checkConsistancy(model_output)

        #perform measurement
        sensor_output = 0
        if self.sensor is not None:
            sensor_output = self.sensor.measure(s.t, self.model_output)
        else:
            sensor_output = model_output

        #get desired values
        traj_output = 0
        if self.trajectory is not None:
            traj_output = self.trajectory.getValues(s.t, self.tOrder)

        #perform control
        self.controller_output = 0
        if self.controller is not None:
            self.controller_output = self.controller.control(sensor_output, traj_output)

        #store
        if self.logger is not None:
            data = {'t':s.t}
            for i in range(self.model.getStates()):
                data.update({('x%i' % (i+1)): model_output[i]})

            self.logger.log(data)

        return model_output
    
# hier wird erst der Reglerausgang mit den Initialwerten ausgerechnet und anschließend in das Modell eingespeist
# damit funktioniert der F- und GController leider auch nicht, die Reglerwerten hauen schon nach dem zweiten 
# Schritt ab
    
#    def calcStep(self):
#        '''
#        Calculate one step in simulation
#        '''
#        s = self.solver
#        
#        if self.start == True:
#            if self.trajectory is not None:
#                traj_output = self.trajectory.getValues(s.t, self.tOrder)
#                print 'im start traj_output: ',traj_output    
#            if self.controller is not None:
#                self.controller_output = self.controller.control(self.q, traj_output)
#                print 'initial state: ', self.q
#                print 'im start: self.controller_output: ',self.controller_output
#            self.start = False
#        else:
#            #get desired values
#            traj_output = 0
#            if self.trajectory is not None:
#                traj_output = self.trajectory.getValues(s.t, self.tOrder)
#            print 'traj_output: ',traj_output            
#            
#            #perform control
#            self.controller_output = 0
#            if self.controller is not None:
#                self.controller_output = self.controller.control(self.sensor_output, traj_output)
#            print 'self.controller_output: ',self.controller_output
#            
#        # integrate model
#        self.model.setInput(self.controller_output)
#        model_output = s.integrate(s.t+dt)
#        print 'model_output: ',model_output
#
#        #check credibility
#        self.model.checkConsistancy(model_output)
#
#        #perform measurement
#        self.sensor_output = 0
#        print 'self.sensor: ',self.sensor
#        if self.sensor is not None:
#            self.sensor_output = self.sensor.measure(s.t, self.model_output)
#        else:
#            self.sensor_output = model_output
#        print 'self.sensor_output: ',self.sensor_output      
#
#        #store
#        if self.logger is not None:
#            data = {'t':s.t}
#            for i in range(self.model.getStates()):
#                data.update({('x%i' % (i+1)): model_output[i]})
#
#            self.logger.log(data)
#
#        return model_output

