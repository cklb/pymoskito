import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class BallBeamModel(pm.Model):
    """
    Implementation of the Ball and Beam System
    """
    public_settings = OrderedDict([("M", st.M),
                                   ("R", st.R),
                                   ("J", st.J),
                                   ("Jb", st.Jb),
                                   ("G", st.G),
                                   ("beam length", st.beam_length),
                                   ("beam width", st.beam_width),
                                   ("beam depth", st.beam_depth),
                                   ("initial state", st.initial_state)
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "ball position", "Unit": "m"},
            1: {"Name": "beam angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.M = self._settings['M']
        self.R = self._settings['R']
        self.J = self._settings['J']
        self.Jb = self._settings['Jb']
        self.G = self._settings['G']
        self.B = self.M / (self.Jb / self.R ** 2 + self.M)

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input tau
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        tau = args[0]

        dx1 = x2
        dx2 = self.B * (x1 * x4 ** 2 - self.G * np.sin(x3))
        dx3 = x4

        # inverse nonlinear system transformation
        u = (tau - self.M * (2 * x1 * x2 * x4
                             + self.G * x1 * np.cos(x3))) / (self.M * x1 ** 2
                                                             + self.J + self.Jb)
        dx4 = u

        return np.array([dx1, dx2, dx3, dx4])

    def root_function(self, x):
        """
        is not used
        :param x: state
        :return:
        """
        return [False]

    def check_consistency(self, x):
        """
        Check if the ball remains on the beam
        :param x: state
        """
        if abs(x[0]) > float(self._settings['beam length']) / 2:
            raise pm.ModelException('Ball fell down.')
        if abs(x[2]) > np.pi / 2:
            raise pm.ModelException('Beam reached critical angle.')

    def calc_output(self, input_vector):
        """
        return ball position as output
        :param input_vector: input values
        :return: ball position
        """
        return input_vector[0]

pm.register_simulation_module(pm.Model, BallBeamModel)
