#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from collections import OrderedDict
from operator import add
import numpy as np

#Qt
from PyQt4 import QtGui
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

class SimulationModule(QObject):
    """ Smallest Unit in Simulation Process
        Provides neccessary functions like output calculation and holds
        all settings is 'settings' all available settings have to be added
        to this dict and have to be known a priori.
    """
    settings = OrderedDict()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def getOutputDimension(self):
        raise Exception()


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
    finished = pyqtSignal(dict)
    failed = pyqtSignal(dict)
        
    #abilities (should match the module names)
    moduleList = ['model', 'solver', 'disturbance', 'sensor', 'observer', 'controller', 'trajectory']


    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def _initStates(self):
        #init fields with known dimension
        self.current_time = 0
        
        #init model output with current state
        self.solver_output = self.solver.settings['initial state']
        
        #init observer
        if hasattr(self, 'observer'):
            self.observer_counter = self.observer.settings['tick divider']
            self.observer.setStepWidth(1/self.solver.settings['measure rate'])
#            self.observer_output = [0] * self.observer.getOutputDimension()

        #init controller
        if hasattr(self, 'controller'):
            if 'tick divider' in self.controller.settings:
                self.controller_counter = self.controller.settings['tick divider']

            self.controller_output = [0] * self.controller.getOutputDimension()

    def _initStorage(self):
        #init fields with fixed dimensions
        self.storage = {\
               'simTime':[],\
               }

    def _calcStep(self):
        '''
        Calcualte one step in simulation
        '''
        self.current_time = self.solver.getTime()

        #write new output
        self.model_output = self.solver_output
        
        #perform disturbance
        if hasattr(self, 'disturbance'):
            self.disturbance_output = self.disturbance.disturb(self.current_time)
        else:
            self.disturbance_output = [0 for i in range(self.model.getOutputDimension())]

        #perform measurement
        if hasattr(self, 'sensor'):
            self.sensor_output = self.sensor.measure(self.current_time,\
                    map(add ,self.model_output, self.disturbance_output))
        else:
            self.sensor_output = map(add ,self.model_output, self.disturbance_output)

        #perform observation
        if hasattr(self, 'observer'):
            if self.observer_counter == self.observer.settings['tick divider']:   
                self.observer_output = self.observer.observe(self.current_time,\
                        self.controller_output, self.sensor_output)
                self.observer_counter = 1
            else:
                self.observer_counter += 1
        else:
            self.observer_output = self.sensor_output

        #get desired values
        if hasattr(self, 'trajectory'):
            self.trajectory_output = self.trajectory.getValues(self.current_time)

        #perform control
        if hasattr(self, 'controller'):
            if 'tick divider' in self.controller.settings:
                if self.controller_counter == self.controller.settings['tick divider']:
                    self.controller_output = self.controller.control(self.observer_output,\
                                                    self.trajectory_output)
                    self.controller_counter = 1
                else:
                    self.controller_counter += 1
                    
            else:
                self.controller_output = self.controller.control(self.observer_output,\
                                                self.trajectory_output)
        else:
            self.controller_output = 0

        # integrate model
        self.solver.setInput(self.controller_output)
        self.solver_output = self.solver.integrate(self.current_time) 

        #check credibility
        self.model.checkConsistancy(self.solver_output)

        return 

    def _storeValues(self):
        self.storage['simTime'].append(self.current_time)
        for module in self.moduleList:
            module_values = getattr(self, module+'_output')
            if np.isscalar(module_values):
                module_values = [module_values]

            for idx, val in enumerate(module_values):
                signalName = module + '_output.' + str(idx)
                if signalName in self.storage:
                    self.storage[signalName].append(val)
                else:
                    self.storage.update({signalName: [val]})
    
    @pyqtSlot()
    def run(self):
        #initialize
        self._initStates()
        self._initStorage()
        self.solver.initialize()

        #simulate
        try:
            while self.current_time <= self.solver.settings['end time']:
                self._calcStep()
                self._storeValues()

        except ModelException as e:
            print 'Simulator.run(): Model ERROR: ', e.args[0]
            self.solver.settings['end time'] = self.current_time
            self.failed.emit(self.storage)
            return

        self.finished.emit(self.storage)
        return

    def listModules(self):
        return self.moduleList
