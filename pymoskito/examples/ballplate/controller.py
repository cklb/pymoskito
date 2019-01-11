# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class LinearController(pm.Controller):
    public_settings = OrderedDict([("source", "system_state"),
                                   ("tick divider", 1),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=1)
        settings.update(output_dim=2)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((2, ))

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        return -st.K @ input_values


pm.register_simulation_module(pm.Controller, LinearController)
