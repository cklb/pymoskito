# -*- coding: utf-8 -*-
from collections import OrderedDict

import numpy as np
import sympy as sp

import pymoskito as pm

from . import settings as st

"""
Feedforward implementations for the ball and beam system
"""


class LinearFeedforward(pm.Feedforward):
    """
    A Feedfoward that compensates the linear part of the system dynamics.
    """

    public_settings = OrderedDict([
        ("r0", 3),
        ("M", st.M),
        ("R", st.R),
        ("J", st.J),
        ("Jb", st.Jb),
        ("G", st.G),
        ("B", st.B),
        ("tick divider", 1)
    ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(input_order=4)
        settings.update(output_dim=1)

        pm.Feedforward.__init__(self, settings)

    def _calc_theta_t(self, rdd):
        theta_t = -rdd / (self._settings["B"] * self._settings["G"])
        return theta_t

    def _feedforward(self, t, yd):
        theta = []

        # need the second derivative of theta
        for i in range(2 + 1):
            theta.append(self._calc_theta_t(yd[i + 2]))

        tau = ((self._settings['M'] * self._settings['r0'] ** 2
                + self._settings['J']
                + self._settings['Jb']) * theta[2]
               + self._settings['M'] * self._settings['G'] * yd[0])

        return tau


pm.register_simulation_module(pm.Feedforward, LinearFeedforward)
