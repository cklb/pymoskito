# -*- coding: utf-8 -*-
import numpy as np
from collections import OrderedDict

import pymoskito as pm


# class begin
class BasicController(pm.Controller):
    public_settings = OrderedDict([("poles", [-2, -2, -2, -2])
                                   ])

    # init
    def __init__(self, settings):
        settings.update(input_order=0)
        settings.update(input_type="system_state")

        pm.Controller.__init__(self, settings)

        # model parameters
        g = 9.81  # gravity [m/s^2]
        M = 4.2774  # cart mass [kg]
        D = 10  # cart friction constant [Ns/m]
        m = 0.3211  # pendulum mass [kg]
        d = 0.023  # pendulum friction constant [Nms]
        l = 0.3533  # pendulum length [m]
        J = 0.072  # pendulum moment of intertia [kg*m^2]

        # the system matrices after linearization in phi=PI
        z = (M + m) * J - (m * l) ** 2
        A = np.array([[0, 0, 1, 0],
                      [0, 0, 0, 1],
                      [0, (m * l) ** 2 * g / z, -J * D / z, m * l * d / z],
                      [0, -(M + m) * m * l * g / z, m * l * D / z,
                       -(M + m) * d / z]
                      ])
        B = np.array([[0],
                      [0],
                      [J / z],
                      [-l * m / z]
                      ])
        C = np.array([[1, 0, 0, 0]])

        # the equilibrium state as a vector
        self._eq_state = np.array([0, np.pi, 0, 0])

        # pole placement of linearized state feedback
        self._K = pm.controltools.place_siso(A, B, self._settings["poles"])
        self._V = pm.controltools.calc_prefilter(A, B, C, self._K)

    # control
    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        x = input_values - self._eq_state
        yd = trajectory_values - self._eq_state[0]
        output = - np.dot(self._K, x) + np.dot(self._V, yd[0])

        return output
