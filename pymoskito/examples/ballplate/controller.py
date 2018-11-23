# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict

import pymoskito as pm
import pymoskito.controltools

from . import settings as st
#import end

class LinearController(pm.Controller):
    """
    Controller created by changing f(x)
    """
    public_settings = OrderedDict([("poles", [-3.1, -3.1, -3.1, -3.1]),
                                   ("source", "system_state"),
                                   ("tick divider", 1),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=2)
        settings.update(input_type=settings["source"])

        pm.Controller.__init__(self, settings)
        self._output = np.zeros((2, ))

        # run pole placement
        self.K = pymoskito.controltools.char_coefficients(self._settings["poles"])

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        # input abbreviations
        x1, x2, x3, x4 = input_values
        yd = trajectory_values
        # self._output = -np.array([-1.14*x3-0.86*x4, 1.14*x1+0.86*x2])
        return -st.K @ input_values
        # return 1

#register
pm.register_simulation_module(pm.Controller, LinearController)