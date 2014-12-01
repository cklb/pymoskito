#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import division
from scipy.integrate import ode
from PyQt4.QtCore import QObject, QThread, pyqtSignal, QTimer

import settings as st

#--------------------------------------------------------------------- 
# Core of the physical simulation
#--------------------------------------------------------------------- 
class SimulationThread(QThread):
    """ Thread that runs the physical simulation
    """

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.timer = QTimer()

    def run(self):
        ''' run simulation 
        '''
        self.timer.start(0)


class Simulator(QObject):
    """ Simulation Wrapper
    
    This Class exceutes the timestep integration.
    """

    finished = pyqtSignal()

    def __init__(self, logger, parent=None):
        QObject.__init__(self, parent)
        self.logger = logger
        
        #init states
        self.traj_output = 0
        self.controller_output = 0
        self.sensor_output = 0
        
    def setupSolver(self, intMode=None, intMethod=None, rTol=None, aTol=None):
        self.solver = ode(model.stateFunc)
        self.solver.set_integrator(intMode, method=intMethod, rtol=rTol, atol=aTol)

    def setInitialValues(self, values):
        if self.solver is None:
            print('Error setup solver first!')
        else:
            self.solver.set_initial_value(values)

    def setTrajectoryGenerator(self, generator):
        self.trajectory = generator
        self.trajectory.newData.connect(logger.log)

    def setController(self, controller):
        self.controller = controller
        self.controller.newData.connect(logger.log)
        self.tOrder = controller.getOrder()

    def setModel(self, model):
        self.model = model
        self.model.newData.connect(logger.log)

    def setSensor(self, sensor):
        self.sensor = sensor
        self.sensor.newData.connect(logger.log)

    def setEndTime(self, endTime):
        self.endTime = endTime

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
        if self.sensor is not None:
            sensor_output = self.sensor.measure(s.t, self.model_output)
        else:
            sensor_output = model_output

        #get desired values
        if self.trajectory is not None:
            traj_output = self.trajectory.getValues(s.t, self.tOrder)

        #perform control
        if self.controller is not None:
            self.controller_output = self.controller.control(sensor_output, traj_output)

        #store
        #if self.logger is not None:
            #data = {'t':s.t}
            #for i in range(self.model.getStates()):
                #data.update({('x%i' % (i+1)): model_output[i]})

            #self.logger.log(data)

        #check end time
        if self.endTime is not None:
            if s.t >= self.endTime:
                emit(finished)


        return model_output
    
