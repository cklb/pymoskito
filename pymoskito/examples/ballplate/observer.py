# -*- coding: utf-8 -*-
from collections import OrderedDict

import numpy as np
import sympy as sp
from scipy.integrate import ode
from sympy import sin, cos

import pymoskito as pm
from pymoskito.tools import swap_cols, swap_rows
from . import settings as st


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
        self.output = np.array(self._settings["initial state"], dtype=float)

    def state_func(self, t, q, args):
        x_o = q
        u = args[0]
        y = args[1]

        dx_o = ((st.A - st.L @ st.C @ st.T) @ x_o
                + st.B_1 @ u
                + st.L @ y)
        return dx_o

    def _observe(self, time, system_input, system_output):
        # np.copyto(self.output, self.next_output)
        if system_input is not None:
            dy = self.state_func(time, self.output,
                                 (system_input, system_output))
            self.output += self.step_width * dy
        return self.output


pm.register_simulation_module(pm.Observer, LuenbergerObserver)
