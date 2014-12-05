#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from collections import OrderedDict

class SimulationModule:
    """ Smallest Unit in Simulation Process
        Provides neccessary functions like output calculation and holds
        all settings is 'settings' all available settings have to be added
        to this dict and have to be known a priori.
    """
    settings = OrderedDict()

    def __init__(self):
        pass

    def getOutputDimension(self):
        raise Exception()

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
class Simulator(QObject):
    """ Simulation Wrapper
    
        This Class exceutes the timestep integration.
    """

    #qt general
    finished = pyqtSignal()
    failed = pyqtSignal()
        
    #abilities (should match the module names)
    moduleList = ['model', 'disturbance', 'sensor', 'observer', 'controller', 'trajectory']

    #solver specific
    solverSettings = {'Mode': 'vode',\
            'Method': 'adams',\
            'step size': 0.01,\
            'rTol': 1e-6,\
            'aTol': 1e-9,\
            'end time': 100,\
            }

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def _initStates(self):
        #init fields with known dimension
        self.states = {\
                'current_time': 0,\
                }

        #init fields with variing names
        for elem in self.modulelist:
            self.states.update({(elem+'_output'): 0})

    def _initStorage(self):
        #init fields with fixed dimensions
        self.storage = {\
               'simTime':[],\
               }

        #init fields with variable dimensions
        for module in self.moduleList:
            for idx in range(len(module.getOutputDimension())):
                self.states.update({(elem+'_output.'+idx): []})

    def _setupSolver(self):
        self.solver = ode(self.model.stateFunc)
        self.solver.set_integrator(self.solverSettings['Mode'],\
                method=self.solverSettings['Method'],\
                rtol=self.solverSettings['rTol'],\
                atol=self.solverSettings['aTol'],\
                ) 
        self.solver.set_initial_value(self.model.settings['initial value'])

    def _calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        
        # integrate model
        self.model.setInput(self.controller_output)
        s = self.solver
        self.simTime = s.t
        self.model_output = s.integrate(s.t + self.solverSettings['step size']) 

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
            self.controller_output = self.controller.control(self.observer_output, self.traj_output)

        return 

    def _storeValues(self):
        self.storage['simTime'].append(self.simTime)
        for module in self.moduleList:
            module_values = getattr(self, module+'_output')
            for idx, val in enumerate(module_values):
                self.storage[elem+'_output.'+idx].append(val)

    def run(self):
        #initialize
        self._initStates()
        self._initStorage()
        self._setupSolver()

        #simulate
        try:
            while self.simTime <= self.solverSettings['end time']:
                self._calcStep()
                self._storeValues()

        except ModelException as e:
            print 'Simulator.run(): Model ERROR: ', e.args[0]
            self.solverSettings['end time'] = self.simTime
            self.failed.emit()
            return

        self.finished.emit()
        return

    def getValues(self):
        return self.storage

    def listModules(self):
        return self.moduleList
