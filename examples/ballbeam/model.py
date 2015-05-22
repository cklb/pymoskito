__author__ = 'stefan'

from collections import OrderedDict
import numpy as np
from pymoskito.simulation_modules import Model, ModelException

import settings as st


class BallBeamModel(Model):
    """
    Implementation of the Ball and Beam System
    """
    public_settings = OrderedDict(M=st.M,
                                  R=st.R,
                                  J=st.J,
                                  Jb=st.Jb,
                                  G=st.G,
                                  beamlength=st.beam_length,
                                  beamwidth=st.beam_width,
                                  beamdepth=st.beam_depth
                                  )

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        Model.__init__(self, settings)

        # shortcuts for readability
        self.M = self.settings['M']
        self.R = self.settings['R']
        self.J = self.settings['J']
        self.Jb = self.settings['Jb']
        self.G = self.settings['G']
        self.B = self.M / (self.Jb / self.R ** 2 + self.M)

    def state_function(self, x, t, *args):
        """
        Calculations of system state changes
        :type args: system input tau
        """
        # assert isinstance(x, object)
        assert isinstance(args, float)

        # definitoric
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        tau = args

        dx1 = x2
        dx2 = self.B * (x1 * x4 ** 2 - self.G * np.sin(x3))
        dx3 = x4

        # inverse nonliniear system transformation
        u = (tau - self.M * (2 * x1 * x2 * x4 + self.G * x1 * np.cos(x3))) / (self.M * x1 ** 2 + self.J + self.Jb)
        dx4 = u

        return [dx1, dx2, dx3, dx4]

    def root_function(self, x):
        return False

    def check_consistency(self, x):
        """
        Check if the ball remains on the beam
        """
        if abs(x[0]) > float(self.settings['beamlength']) / 2:
            raise ModelException('Ball fell down.')
        if abs(x[2]) > np.pi / 2:
            raise ModelException('Beam reached critical angle.')

