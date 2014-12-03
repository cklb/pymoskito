#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from scipy.integrate import ode

#Qt
from PyQt4 import QtGui
from PyQt4.QtCore import QObject, pyqtSignal

#own
from model import ModelException
import settings as st

#--------------------------------------------------------------------- 
# Core of the physical simulation
#--------------------------------------------------------------------- 
class SimulationModule():
    """ Smallest Unit in Simulation Process
        Provides neccessary functions like output calculation and holds
        all settings
    """
    settings = {}

    def __init__(self):
        pass

    def getOutputDimension(self)
        raise Exception()


class Simulator(QObject):
    """ Simulation Wrapper
    
        This Class exceutes the timestep integration.
    """

    #qt general
    finished = pyqtSignal()
    failed = pyqtSignal()
        
    #abilities (should match the module names)
    moduleList = ['model', 'disturbance', 'sensor', 'observer', 'control', 'trajectory']

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def initStates(self):
        #init fields with known dimension
        self.states = {\
                'current_time': 0,\
                }

        #init fields with variing names
        for elem in self.modulelist:
            self.states.update({(elem+'_output'): 0})

    def initStorage(self):
        #init fields with fixed dimensions
        self.storage = {\
               'simTime':[],\
               }

        #init fields with variable dimensions
        for module in self.moduleList:
            for idx in range(len(module.getOutputDimension())):
                self.states.update({(elem+'_output.'+idx): []})

    def setupSolver(self):
        self.solver = ode(self.model.stateFunc)
        self.solver.set_integrator(self.solverSettings['Mode'],\
                method=self.solverSettings['Method'],\
                rtol=self.solverSettings['rTol'],\
                atol=self.solverSettings['aTol'],\
                } 
        self.solver.set_initial_value(self.initialValues)

    def calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        
        # integrate model
        self.model.setInput(self.controller_output)
        s = self.solver
        self.model_output = s.integrate(s.t+self.stepSize) 
        self.simTime = s.t

        #check credibility
        self.model.checkConsistancy(self.model_output)

        # --- run simulation modules ---
        
        #perform disturbance
        if hasattr(self, 'disturbance'):
            self.disturbance_output = self.disturbance.disturb(s.t)
        else:
            self.disturbance_output = 0

        #perform measurement
        if hasattr(self, 'sensor'):
            self.sensor_output = self.sensor.measure(s.t,\
                    self.model_output + self.disturbance_output)
        else:
            self.sensor_output = self.model_output

        #perform observation
        if hasattr(self, 'observer'):
            self.observer_output = self.oberver.observe(self.sensor_output)
        else:
            self.observer_output = self.sensor_output

        #get desired values
        if hasattr(self, 'trajectory'):
            self.traj_output = self.trajectory.getValues(s.t, self.tOrder)

        #perform control
        if hasattr(self, 'controller'):
            self.controller_output = self.control.control(self.observer_output, self.traj_output)

        return 

    def storeValues(self):
        self.storage['simTime'].append(self.simTime)
        for module in self.moduleList:
            module_values = getattr(self, module+'_output')
            for idx, val in enumerate(module_values)
                self.storage[elem+'_output.'+idx].append(val)

    def run(self):
        #initialize
        self.initStates()
        self.initStorage()
        self.setupSolver()

        #simulate
        try:
            while self.simTime <= self.endTime:
                self.calcStep()
                self.storeValues()

        except ModelException as e:
            print 'Simulator.run(): Model ERROR: ', e.args[0]
            self.endTime = self.simTime
            self.failed.emit()
            return

        self.finished.emit()
        return

    def getValues(self):
        return self.storage

    def listModules(self):
        return self.moduleList
