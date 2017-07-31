# -*- coding: utf-8 -*-

import numpy as np
from collections import OrderedDict

import pymoskito as pm


class OpenLoop(pm.Controller):
    """
    manual pwm input
    """
    public_settings = OrderedDict([("pwm", 160),
                                   ("tick divider", 1)])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=0)
        settings.update(output_dim=1)
        settings.update(input_type="system_state")

        pm.Controller.__init__(self, settings)

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):

        u = self._settings["pwm"]
        return np.array(u)

pm.register_simulation_module(pm.Controller, OpenLoop)
