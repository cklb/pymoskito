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
    
    Keyword Args:
        type: Keyword describing the state change, can be one of the following
        
            * `init` Initialisation
            * `start` : Start of Simulation
            * `time` : Accomplishment of new progress step
            * `finish` : Finish of Simulation
            * `abort` : Abortion of Simulation
            
        data: Data that is emitted on state change.
        info: Further information.
        
    """

    def __init__(self, **kwargs):

        assert "type" in kwargs.keys()
        for key, val in kwargs.items():
            setattr(self, key, val)


class SimulationSettings(object):
    def __init__(self, start_time, end_time, step_size, measure_rate):
        self.start_time = start_time
        self.end_time = end_time
        self.step_size = step_size
        self.measure_rate = measure_rate

    def to_dict(self):
        return {
            "start time": self.start_time,
            "end time": self.end_time,
            "step size": self.step_size,
            "measure rate": self.measure_rate,
        }


class Simulator(QObject):
    """ 
    This Class executes the time-step integration.

    It forms the Core of the physical simulation and interacts with the GUI
    via the :py:class:''SimulationInterface`

    Calculated values will be stored every 1 / measure rate seconds.
    """

    work_done = pyqtSignal()
    state_changed = pyqtSignal(SimulationStateChange)

    # list of modules that have to appear in every run
    static_module_list = [
        "Model",
        "Solver"
    ]

    # list of modules that might not always appear but have to be calculated
    # in a special order
    _dynamic_module_list = [
        "Disturbance",
        "Sensor",
        "ObserverMixer",
        "Observer",
        "Trajectory",
        "Feedforward",
        "Controller",
        "ModelMixer",
        "Limiter",
    ]

    module_list = static_module_list + _dynamic_module_list

    def __init__(self, settings, modules):
        QObject.__init__(self, None)
        self._run = False
        self._logger = logging.getLogger(self.__class__.__name__)

        assert isinstance(settings, SimulationSettings)
        self._settings = settings
        assert isinstance(modules, dict)
        self._simulation_modules = modules

        self._init_states()
        self._init_settings()
        self.updated_time = 0
        self._storage = dict()

    def _init_states(self):
        self._input_vector = {}
        self._counter = {}
        self._current_outputs = {}
        self._current_outputs.update(time=self._settings.start_time)

        for mod_name, obj in self._simulation_modules.items():
            self._counter.update({mod_name: obj.tick_divider})
            self._current_outputs.update({mod_name: []})
            self._current_outputs[mod_name] = []

        # init model output with current state
        self._simulation_modules["Solver"].next_output = np.array(
            self._simulation_modules["Model"].initial_state)

    def _init_settings(self):
        """ Initialize module settings that depend on other modules.
        """
        # calculate the correct step width for every block
        for mod_name, obj in self._simulation_modules.items():
            obj.step_width = obj.tick_divider * self._settings.step_size

        return

    def _calc_module(self, module_name):
        """ Calculates the output of a simulation module
        """
        if module_name in self._simulation_modules.keys():
            if self._counter[module_name] == \
                    self._simulation_modules[module_name].tick_divider:
                self._current_outputs[module_name] = np.atleast_1d(
                    self._simulation_modules[module_name].calc_output(
                        self._input_vector))
                self._counter[module_name] = 1
            else:
                self._counter[module_name] += 1

            # update input vector
            self._input_vector.update(
                {module_name: self._current_outputs[module_name]})

    def _calc_step(self):
        """
        Calculate one step in simulation.
        
        Warn:
            Due to the observers need for the last system input, the values of
            the last step are kept in the input vector until they are 
            overridden. Be careful about which value is needed at which place or
            otherwise you end up using a value from the last step.
        """
        # update time and current state
        self._current_outputs["time"] = self._simulation_modules["Solver"].t
        self._input_vector.update(
            time=self._current_outputs["time"],
            system_state=np.atleast_1d(
                self._simulation_modules["Solver"].next_output)
        )

        # apply new output
        self._current_outputs["Model"] = np.atleast_1d(
            self._simulation_modules["Model"].calc_output(
                self._input_vector["system_state"]))
        self._input_vector.update(system_output=self._current_outputs["Model"])

        # compute all dynamic modules
        for mod in self._dynamic_module_list[1:]:
            self._calc_module(mod)

        # integrate model
        self._choose_system_input(self._input_vector)
        self._calc_module("Solver")

        if 0:
            # calculate system state changes
            self._current_outputs["State_Changes"] = \
                self._simulation_modules["Model"]\
                    .state_function(self._current_outputs["time"],
                                    self._current_outputs["Solver"],
                                    self._current_outputs["ModelMixer"])

        return

    def _choose_system_input(self, input_vector):
        """ This is mainly done for convenience.
        """
        if "Limiter" in input_vector:
            _input = input_vector["Limiter"]
        elif "ModelMixer" in input_vector:
            _input = input_vector["ModelMixer"]
        elif "Controller" in input_vector:
            if "Feedforward" in input_vector:
                raise SimulationException(
                    "Controller and Feedforward present but no"
                    "ModelMixer. Ambiguous Situation")
            _input = input_vector["Controller"]
        elif "Feedforward" in input_vector:
            _input = input_vector["Feedforward"]
        else:
            raise SimulationException("No system input given.")

        self._input_vector["system_input"] = _input

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
        Start the simulation.
        """
        self._run = True
        self.state_changed.emit(SimulationStateChange(type="start"))

        first_run = True
        rate = 1 / self._settings.measure_rate
        solver = self._simulation_modules["Solver"]

        while self._current_outputs["time"] < self._settings.end_time:
            t = solver.t
            dt = 0
            while dt < rate:
                if not self._run:
                    self._abort("Simulation aborted by user")
                    break

                try:
                    self._calc_step()

                except Exception as e:
                    # catch all to avoid loosing data
                    self._abort(sys.exc_info())
                    break

                dt = solver.t - t
                if dt < rate and first_run:
                    self._store_values()
                first_run = False

            self._store_values()
            self._check_time()

        self._finish()

    def _abort(self, info):
        """ Overwrite end time with reached time.
        """
        self._settings.end_time = self._current_outputs["time"]
        self._storage.update(finished=False)
        end_state = "abort"
        self.state_changed.emit(SimulationStateChange(type=end_state,
                                                      data=self.output,
                                                      info=info))

    def _finish(self):
        self._storage.update(finished=True)
        end_state = "finish"
        self.state_changed.emit(SimulationStateChange(type=end_state,
                                                      data=self.output,
                                                      info="Success"))
        self.work_done.emit()

    @pyqtSlot(name="stop")
    def stop(self):
        """ Stop the simulation. """
        self._run = False

    @property
    def output(self):
        # convert storage entries
        out = dict(modules={}, simulation={}, results={})

        for mod, results in self._storage.items():
            # grab module settings
            if mod in self._simulation_modules:
                out["modules"].update(
                    {mod: self._simulation_modules[mod].settings})

            # grab module data
            if not isinstance(results, list):
                # flag or string -> nothing to convert
                entry = results
            elif isinstance(results[0], np.ndarray):
                # convert list of 1d-arrays into 2d-array
                entry = np.array(results)
            else:
                # convert list of scalars into 1d-array
                entry = np.array(results)
            out["results"].update({mod: entry})

        # grab simulator settings
        out.update({"simulation": self._settings.to_dict()})
        return out

    @property
    def settings(self):
        return self._settings.to_dict()
