# -*- coding: utf-8 -*-


import logging
import sys

import numpy as np
from copy import deepcopy
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from .simulation_modules import SimulationException


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
        for key, val in kwargs.items():
            setattr(self, key, val)


class SimulationSettings(object):
    def __init__(self, start_time, end_time, measure_rate):
        self.start_time = start_time
        self.end_time = end_time
        self.measure_rate = measure_rate

    def to_dict(self):
        return {
            "start time": self.start_time,
            "end time": self.end_time,
            "measure rate": self.measure_rate,
        }


class Simulator(QObject):
    """ Simulation Wrapper
        This Class executes the timestep integration.
        It forms the Core of the physical simulation
        Calculated values will be stored every 1 / measure rate seconds.
    """

    finished = pyqtSignal()
    state_changed = pyqtSignal(SimulationStateChange)

    # list of modules that have to appear in every run
    _static_module_list = [
        "Model",
        "Solver"
    ]

    # list of modules that might not always appear but have to be calculated in special order
    _dynamic_module_list = [
        "Disturbance",
        "Sensor",
        "ObserverMixer",
        "Observer",
        "Trajectory",
        "Controller",
        "Feedforward",
        "ModelMixer",
        "Limiter",
    ]

    module_list = _static_module_list + _dynamic_module_list

    def __init__(self, settings, modules):
        QObject.__init__(self, None)
        self._logger = logging.getLogger(self.__class__.__name__)

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
        for mod_name, obj in self._simulation_modules.items():
            self._counter.update({mod_name: obj.tick_divider})
            self._current_outputs.update({mod_name: []})
            self._current_outputs[mod_name] = []

        # init model output with current state
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

            # update input vector
            self._input_vector.update({module_name: self._current_outputs[module_name]})

    def _calc_step(self):
        """
        Calculate one step in simulation
        """
        # update time and current state
        self._current_outputs["time"] = self._simulation_modules["Solver"].t
        self._input_vector = dict(time=self._current_outputs["time"],
                                  system_state=self._current_outputs["Solver"]
                                  .reshape(self._current_outputs["Solver"].shape[0], 1))

        # apply new output
        self._current_outputs["Model"] = \
            self._simulation_modules["Model"].calc_output(self._input_vector["system_state"])
        self._input_vector.update(system_output=self._current_outputs["Model"])

        # compute all dynamic modules
        for mod in self._dynamic_module_list[1:]:
            self._calc_module(mod)

        # integrate model
        self._calc_module("Solver")

        # calculate system state changes
        self._current_outputs["State_Changes"] = \
            self._simulation_modules["Model"]\
                .state_function(self._current_outputs["time"],
                                self._current_outputs["Solver"],
                                self._current_outputs["ModelMixer"])

        return

    def _store_values(self):
        """
        store all values of finished integration step
        """
        for key, val in self._current_outputs.items():
            if key in self._storage:
                self._storage[key].append(np.array(val))
            else:
                self._storage.update({key: [np.array(val)]})

        return

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
        """
        worker function of simulator.
        call to start simulation
        """

        self.state_changed.emit(SimulationStateChange(type="start"))
        end_state = None
        info = None

        # TODO store values for timestamp t=0, store initial states for model and observer

        solver = self._simulation_modules["Solver"]
        while self._current_outputs["time"] < self._settings.end_time:
            t = solver.t
            dt = 0
            while dt < 1 / self._settings.measure_rate:
                try:
                    self._calc_step()
                    dt = solver.t - t

                except Exception as e:
                    # overwrite end time with reached time
                    self._settings.end_time = self._current_outputs["time"]
                    self._storage.update(finished=False)
                    end_state = "abort"
                    info = sys.exc_info()
                    break

            self._store_values()
            self._check_time()

        if end_state is None:
            self._storage.update(finished=True)
            end_state = "finish"

        self.state_changed.emit(SimulationStateChange(type=end_state, data=self.output, info=info))
        self.finished.emit()

    @property
    def output(self):
        # convert storage entries
        out = {}
        for module, results in self._storage.items():
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

        out.update({"Simulation": self._settings.to_dict()})
        return out

    @property
    def settings(self):
        return self._settings.to_dict()
