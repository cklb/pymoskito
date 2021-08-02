# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np

import pymoskito as pm


class CppPIDController(pm.Controller, pm.CppBinding):
    """
    PID Controller implemented in cpp with pybind11
    """
    public_settings = OrderedDict([
        ("Kp", 12),
        ("Ti", 12),
        ("Td", 12),
        ("dt", 0.1),
        ("output_limits", [0, 255]),
        ("input_state", [0]),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        pm.Controller.__init__(self, settings)
        pm.CppBinding.__init__(self, module_name='PIDController', module_path=__file__)

        self.lastTime = 0
        self.lastU = 0

        self.pid = self.get_module_instance('PIDController')()
        self.pid.create(self._settings["Kp"],
                        self._settings["Ti"],
                        self._settings["Td"],
                        self._settings["output_limits"][0],
                        self._settings["output_limits"][1],
                        self._settings['dt'])

    def _control(self,
                 time,
                 trajectory_values=None,
                 feedforward_values=None,
                 input_values=None,
                 **kwargs):
        # step size
        dt = time - self.lastTime

        # input abbreviations
        x = np.zeros((len(self._settings["input_state"]),))
        for idx, state in enumerate(self._settings["input_state"]):
            x[idx] = input_values[int(state)]

        if np.isclose(dt, self._settings['dt']):
            # save last control time
            self.lastTime = time

            yd = trajectory_values

            u = np.array([self.pid.compute(x, yd)])
        else:
            u = self.lastU

        self.lastU = u

        return u


pm.register_simulation_module(pm.Controller, CppPIDController)
