# -*- coding: utf-8 -*-

import numpy as np
from collections import OrderedDict

import pymoskito as pm


class LuenbergerObserver(pm.Observer):
    """
    Luenberger Observer that uses a simple euler forward integration
    """
    public_settings = OrderedDict([
        ("initial state", [0, 0, 0, 0]),
        ("poles", [-20, -20, -20, -20]),
        ("steady state", [0, 0, 0, 0]),
        ("steady tau", 0),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        settings.update(output_dim=4)
        super().__init__(settings)

        self.a_mat, self.b_mat, self.c_mat = linearise_system(
            self._settings["steady state"],
            self._settings["steady tau"])
        self.L = pm.place_siso(self.a_mat.T,
                               self.c_mat.T,
                               self._settings["poles"]).T
        self.output = np.array(self._settings["initial state"], dtype=float)

    def state_func(self, t, q, args):
        x_o = q
        u = args[0]
        y = args[1]

        dx_o = ((self.a_mat - self.L @ self.c_mat) @ x_o
                + self.b_mat @ u
                + self.L @ y)
        return dx_o

    def _observe(self, time, system_input, system_output):
        # np.copyto(self.output, self.next_output)
        if system_input is not None:
            dy = self.state_func(time, self.output,
                                 (system_input, system_output))
            self.output += self.step_width * dy
        return self.output


class CppLuenbergerObserver(pm.CppObserver):
    """
    Luenberger Observer that uses a simple euler forward integration
    """
    public_settings = OrderedDict([
        ("initial state", [0, 0, 0, 0]),
        ("poles", [-20, -20, -20, -20]),
        ("steady state", [0, 0, 0, 0]),
        ("steady tau", 0),
        ("tick divider", 1),
    ])

    def __init__(self, settings):
        settings.update(output_dim=4)
        super().__init__(settings)

        self.a_mat, self.b_mat, self.c_mat = linearise_system(
            self._settings["steady state"],
            self._settings["steady tau"])
        self.L = pm.place_siso(self.a_mat.T,
                               self.c_mat.T,
                               self._settings["poles"]).T
        self.output = np.array(self._settings["initial state"], dtype=float)

    def state_func(self, t, q, args):
        x_o = q
        u = args[0]
        y = args[1]

        dx_o = ((self.a_mat - self.L @ self.c_mat) @ x_o
                + self.b_mat @ u
                + self.L @ y)
        return dx_o

    def _observe(self, time, system_input, system_output):
        # np.copyto(self.output, self.next_output)
        if system_input is not None:
            dy = self.state_func(time, self.output,
                                 (system_input, system_output))
            self.output += self.step_width * dy
        return self.output


pm.register_simulation_module(pm.Observer, LuenbergerObserver)
pm.register_simulation_module(pm.Observer, CppLuenbergerObserver)
