# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from simulation_modules import SimulationException


class SimulationStateChange(object):
    """
    Object that is emitted when Simulator changes its state.
    This happens on:
        - Initialisation
        - Start of Simulation
        - Accomplishment of new progress step
        - Finish of Simulation
        - Abortion of Simulation
    """
    def __init__(self, **kwargs):
        assert "type" in kwargs.keys()
        for key, val in kwargs.iteritems():
            setattr(self, key, val)


class SimulationSettings:
    def __init__(self, start_time, end_time, measure_rate):
        self.start_time = start_time
        self.end_time = end_time
        self.measure_rate = measure_rate


class Simulator(QObject):
    """ Simulation Wrapper
        This Class executes the timestep integration.
        It forms the Core of the physical simulation
        Calculated values will be stored every 1 / measure rate seconds.
    """

    finished = pyqtSignal()
    state_changed = pyqtSignal(SimulationStateChange)

    # abilities (should match the module names)
    module_list = ['Model',
                   'Solver',
                   # 'disturbance',
                   # 'sensor',
                   # 'observer',
                   'Controller',
                   # 'feedforward',
                   # 'limiter',
                   'Trajectory'
                   ]

    def __init__(self, settings, modules):
        QObject.__init__(self, None)
        assert isinstance(settings, SimulationSettings)
        self._settings = settings
        assert isinstance(modules, dict)
        self._simulation_modules = modules

        self._init_states()
        self.updated_time = 0
        self._storage = dict()

    def _init_states(self):
        self._input_vector = {}
        self._counter = {}
        self._current_outputs = {}
        self._current_outputs.update(time=0)
        for mod_name, obj in self._simulation_modules.iteritems():
            self._counter.update({mod_name: obj.tick_divider})
            self._current_outputs.update({mod_name: []})
            # TODO think whether it is needed more specific (output dimension)
            self._current_outputs[mod_name] = []

        # init model output with current state
        # TODO make use of start time setting
        self._current_outputs["Solver"] = self._simulation_modules["Model"].initial_state

        return

        # TODO special init for other blocks
        # init observer
        # if hasattr(self, 'observer'):
        #     self.observer_counter = self.observer.settings['tick divider']
        #     self.observer.setStepWidth(1 / self.solver.settings['measure rate'])

        # init feedforward
        # if hasattr(self, 'feedforward'):
        #     self.feedforward.setStepWidth(1 / self.solver.settings['measure rate'])

    def _calc_module(self, module_name):
        """
        calculates the output of a simulation module
        """
        if module_name in self._simulation_modules.keys():
            if self._counter[module_name] == self._simulation_modules[module_name].tick_divider:
                self._current_outputs[module_name] = \
                    self._simulation_modules[module_name].calc_output(self._input_vector)
                self._counter[module_name] = 1
            else:
                self._counter[module_name] += 1
        else:
            self._current_outputs[module_name] = 0

        # update input vector
        self._input_vector.update({module_name: self._current_outputs[module_name]})

    def _calc_step(self):
        """
        Calculate one step in simulation
        """
        # update time and current state
        self._current_outputs["time"] = self._simulation_modules["Solver"].t
        self._input_vector = dict(time=self._current_outputs["time"],
                                  system_state=self._current_outputs["Solver"])

        # apply new output
        self._current_outputs["Model"] = \
            self._simulation_modules["Model"].calc_output(self._input_vector["system_state"])
        self._input_vector.update(system_output=self._current_outputs["Model"])

        # # perform disturbance
        # if hasattr(self, 'disturbance'):
        #     self.disturbance_output = self.disturbance.disturb(self.current_time)
        # else:
        #     self.disturbance_output = [0 for i in range(self.model.getOutputDimension())]
        #
        # # perform measurement
        # if hasattr(self, 'sensor'):
        #     self.sensor_output = self.sensor.measure(self.current_time,
        #                                              map(add, self.model_output, self.disturbance_output))
        # else:
        #     self.sensor_output = map(add, self.model_output, self.disturbance_output)

        # perform observation
        self._calc_module("Observer")

        # get desired values
        self._calc_module("Trajectory")

        # perform control
        self._calc_module("Controller")

        # # get feedforward values
        # # TODO remember that this signal can be vector, too.
        # if hasattr(self, 'feedforward'):
        #     self.feedforward_output = self.feedforward.feed(self.trajectory_output)
        # else:
        #     self.feedforward_output = 0

        # # perform limitation
        # if hasattr(self, 'limiter'):
        #     self.limiter_output = self.limiter.limit(self.feedforward_output + self.controller_output)
        # else:
        #     self.limiter_output = self.feedforward_output + self.controller_output

        # integrate model
        self._calc_module("Solver")

        return

    def _store_values(self):
        """
        store all values of finished integration step
        """
        for key, val in self._current_outputs.iteritems():
            if key in self._storage:
                self._storage[key].append(val)
            else:
                self._storage.update({key: [val]})

        return

        self._storage['simTime'].append(self.current_time)
        for module in self.module_list:
            module_values = getattr(self, module + '_output')
            if np.isscalar(module_values):
                module_values = [module_values]

            for idx, val in enumerate(module_values):
                signal_name = module + '_output.' + str(idx)
                # print 'Signal: ', signal_name, type(val)
                if signal_name in self._storage:
                    self._storage[signal_name].append(float(val))
                else:
                    self._storage.update({signal_name: [float(val)]})

    def _check_time(self):
        """
        send update notification every second
        """
        t = self._current_outputs["time"]
        if t - self.updated_time > 1:
            self.state_changed.emit(SimulationStateChange(type="time", t=t))
            # self.timeChanged.emit(t)
            self.updated_time = t

    @pyqtSlot()
    def run(self):

        end_state = None
        try:
            while self._current_outputs["time"] <= self._settings.end_time:
                t = self._simulation_modules["Solver"].t
                dt = 0
                while dt < 1/self._settings.measure_rate:
                    self._calc_step()
                    dt = self._simulation_modules["Solver"].t - t

                self._store_values()
                self._check_time()

            self._storage.update(finished=True)
            end_state = "finish"

        except SimulationException as e:
            print 'Simulator.run(): Model ERROR: ', e.args[0]
            # overwrite end time with reached time
            self._settings["end time"] = self._current_outputs["time"]
            self._storage.update(finished=False)
            end_state = "abort"

        finally:
            self.state_changed.emit(SimulationStateChange(type=end_state, data=self.output))
            self.finished.emit()

    @property
    def output(self):
        # convert storage entries
        out = {}
        for module, results in self._storage.iteritems():
                if not isinstance(results, list):
                    # flag or string -> nothing to convert
                    entry = results
                elif isinstance(results[0], np.ndarray):
                    # convert list of 1d-arrays into 2d-array
                    entry = np.array(results)
                else:
                    # convert list of scalars into 1d-array
                    entry = np.array(results)
                out.update({module: entry})

        return out

    def list_modules(self):
        return self.module_list

    @property
    def settings(self):
        return self._settings
