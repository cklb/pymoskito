# -*- coding: utf-8 -*-
from __future__ import division
from operator import add
import numpy as np
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from simulation_modules import ModelException


class Simulator(QObject):
    """ Simulation Wrapper
        This Class executes the timestep integration.
        It forms the Core of the physical simulation
    """

    finished = pyqtSignal(dict)
    failed = pyqtSignal(dict)
    timeChanged = pyqtSignal(float)

    # abilities (should match the module names)
    module_list = ['model',
                   'solver',
                   # 'disturbance',
                   # 'sensor',
                   # 'observer',
                   'controller',
                   # 'feedforward',
                   # 'limiter',
                   # 'trajectory'
                   ]

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def _init_states(self):
        self.current_time = 0

        # init model output with current state
        self.solver_output = self.solver.settings['initial state']

        # init observer
        if hasattr(self, 'observer'):
            self.observer_counter = self.observer.settings['tick divider']
            self.observer.setStepWidth(1 / self.solver.settings['measure rate'])

        # init feedforward
        if hasattr(self, 'feedforward'):
            self.feedforward.setStepWidth(1 / self.solver.settings['measure rate'])

        # init controller
        if hasattr(self, 'controller'):
            self.controller.setStepWidth(1 / self.solver.settings['measure rate'])
            if 'tick divider' in self.controller.settings:
                self.controller_counter = self.controller.settings['tick divider']

            self.controller_output = 0 * self.controller.getOutputDimension()
        else:
            self.controller_output = 0

    def _init_storage(self):
        # init fields with fixed dimensions
        self.storage = {
            'simTime': [],
        }
        self.updated_time = 0

    def _calc_step(self):
        """
        Calculate one step in simulation
        """
        self.current_time = self.solver.getTime()

        # write new output
        self.model_output = self.solver_output

        # perform disturbance
        if hasattr(self, 'disturbance'):
            self.disturbance_output = self.disturbance.disturb(self.current_time)
        else:
            self.disturbance_output = [0 for i in range(self.model.getOutputDimension())]

        # perform measurement
        if hasattr(self, 'sensor'):
            self.sensor_output = self.sensor.measure(self.current_time,
                                                     map(add, self.model_output, self.disturbance_output))
        else:
            self.sensor_output = map(add, self.model_output, self.disturbance_output)

        # perform observation
        if hasattr(self, 'observer'):
            if self.observer_counter == self.observer.settings['tick divider']:
                self.observer_output = self.observer.observe(self.current_time,
                                                             self.controller_output, self.sensor_output)
                self.observer_counter = 1
            else:
                self.observer_counter += 1
        else:
            self.observer_output = self.sensor_output

        # get desired values
        if hasattr(self, 'trajectory'):
            self.trajectory_output = self.trajectory.getValues(self.current_time)

        # perform control
        if hasattr(self, 'controller'):
            if 'tick divider' in self.controller.settings:
                if self.controller_counter == self.controller.settings['tick divider']:
                    self.controller_output = self.controller.control(self.observer_output,
                                                                     self.trajectory_output)
                    self.controller_counter = 1
                else:
                    self.controller_counter += 1

            else:
                self.controller_output = self.controller.control(self.observer_output,
                                                                 self.trajectory_output)
        else:
            self.controller_output = 0

        # get feedforward values
        # TODO remember that this signal can be vector, too.
        if hasattr(self, 'feedforward'):
            self.feedforward_output = self.feedforward.feed(self.trajectory_output)
        else:
            self.feedforward_output = 0

        # perform limitation
        if hasattr(self, 'limiter'):
            self.limiter_output = self.limiter.limit(self.feedforward_output + self.controller_output)
        else:
            self.limiter_output = self.feedforward_output + self.controller_output

        # integrate model
        self.solver.setInput(self.limiter_output)
        self.solver_output = self.solver.integrate(self.current_time)

        # check credibility
        self.model.checkConsistancy(self.solver_output)

        return

    def _store_values(self):
        """
        store all values of finished integration step
        """
        self.storage['simTime'].append(self.current_time)
        for module in self.module_list:
            module_values = getattr(self, module + '_output')
            if np.isscalar(module_values):
                module_values = [module_values]

            for idx, val in enumerate(module_values):
                signal_name = module + '_output.' + str(idx)
                # print 'Signal: ', signal_name, type(val)
                if signal_name in self.storage:
                    self.storage[signal_name].append(float(val))
                else:
                    self.storage.update({signal_name: [float(val)]})

    def _check_time(self):
        if self.current_time - self.updated_time > 1:
            self.timeChanged.emit(self.current_time)
            self.updated_time = self.current_time

    @pyqtSlot()
    def run(self):
        # initialize
        self._init_states()
        self._init_storage()
        self.solver.initialize()

        # simulate
        try:
            while self.current_time <= self.solver.settings['end time']:
                # TODO implement inner loop to reduce amount of stored data
                self._calc_step()
                self._store_values()
                self._check_time()

        except ModelException as e:
            print 'Simulator.run(): Model ERROR: ', e.args[0]
            self.solver.settings['end time'] = self.current_time
            self.storage.update(finished=False)
            self.failed.emit(self.storage)
            return

        self.storage.update(finished=True)
        self.finished.emit(self.storage)
        return

    def list_modules(self):
        return self.module_list
