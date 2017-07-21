import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class BallInTubeModel(pm.Model):
    """
    Model of the Ball in Tube System
    """
    public_settings = OrderedDict([('initial state', st.initial_state),
                                   ('d_B', st.d_B),
                                   ('d_R', st.d_R),
                                   ('tube_length', st.tube_length),
                                   ('k_L', st.k_L),
                                   ('k_V', st.k_V),
                                   ('k_s', st.k_s),
                                   ('d', st.d),
                                   ('T', st.T),
                                   ('m', st.m),
                                   ('g', st.g),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "ball elevation", "Unit": "m"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.d_B = self._settings['d_B']
        self.d_R = self._settings['d_R']
        self.tube_length = self._settings['tube_length']
        self.k_L = self._settings['k_L']
        self.k_V = self._settings['k_V']
        self.k_s = self._settings['k_s']
        self.d = self._settings["d"]
        self.T = self._settings['T']
        self.m = self._settings['m']
        self.g = self._settings['g']
        self.A_B = np.pi*self.d_B**2/4
        self.A_R = np.pi*self.d_R**2/4
        self.A_Sp = self.A_R - self.A_B

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input u
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        # x3 = x[2] is not used
        x4 = x[3]
        u = args[0]

        dx1 = x2
        dx2 = -x1/self.T**2 - 2*self.d*x2/self.T + self.k_s*u*st.Vcc/(255*self.T**2)
        dx3 = x4
        dx4 = (self.k_L*((self.k_V*x1 - self.A_B*x4)/self.A_Sp)**2 - self.m*self.g)/self.m

        return np.array([dx1, dx2, dx3, dx4])

    def root_function(self, x):
        """
        in this case this means zero crossing detection for the balls elevation.
        :param x: state
        """
        x0 = x
        flag = False

        if x[2] <= 0:
            x0[2] = 0
            x0[3] = 0
            flag = True

        if x[0] <= 0:
            x0[0] = 0
            x0[1] = 0
            flag = True

        return flag, x0

    def check_consistency(self, x):
        """
        Checks if the model rules are violated
        :param x: state
        """
        if x[2] > (self._settings['tube_length']):  # + self._settings['tube_length']*0.2):
            raise pm.ModelException('Ball flew out of the tube')

    def calc_output(self, input_vector):
        """
        return ball position as output
        :param input_vector: input values
        :return: ball position
        """
        return input_vector[2]


class BallInTubeSpringModel(pm.Model):
    """
    Implementation of the Ball in Tube System with a spring on the bottom
    """
    public_settings = OrderedDict([('initial state', st.initial_state),
                                   ('d_B', st.d_B),
                                   ('d_R', st.d_R),
                                   ('tube_length', st.tube_length),
                                   ('k_L', st.k_L),
                                   ('k_V', st.k_V),
                                   ('k_s', st.k_s),
                                   ('d', st.d),
                                   ('T', st.T),
                                   ('m', st.m),
                                   ('g', st.g),
                                   ('K', st.K),
                                   ('D', st.D),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=1)
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.d_B = self._settings['d_B']
        self.d_R = self._settings['d_R']
        self.tube_length = self._settings['tube_length']
        self.k_L = self._settings['k_L']
        self.k_V = self._settings['k_V']
        self.k_s = self._settings['k_s']
        self.d = self._settings['d']
        self.T = self._settings['T']
        self.m = self._settings['m']
        self.g = self._settings['g']
        self.K = self._settings['K']
        self.D = self._settings['D']
        self.A_B = np.pi*self.d_B**2/4
        self.A_R = np.pi*self.d_R**2/4
        self.A_Sp = self.A_R - self.A_B

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input u
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        u = args[0]

        dx1 = x2
        dx2 = -x1/self.T**2 - 2*self.d*x2/self.T + self.k_s*u*12/(255*self.T**2)
        dx3 = x4

        if x3 < 0:
            # realize a extra spring with spring stiffness K and spring damping D
            dx4 = -(self.K*x3)/self.m - (self.D*x4)/self.m \
                  + (self.k_L*((self.k_V*x1 - self.A_B*x4)/self.A_Sp)**2)/self.m - self.g
        else:
            dx4 = (self.k_L*((self.k_V*x1 - self.A_B*x4)/self.A_Sp)**2)/self.m - self.g

        return np.array([dx1, dx2, dx3, dx4])

    def root_function(self, x):
        """
        in this case this means zero crossing detection for the balls elevation.
        :param x: state
        """
        x0 = x
        flag = False

        # fan speed
        if x[0] <= 0:
            x0[0] = 0
            x0[1] = 0
            flag = True

        return flag, x0

    def check_consistency(self, x):
        """
        Checks if the model rules are violated
        :param x: state
        """
        if x[2] > (self._settings['tube_length']):  # + self._settings['tube_length']*0.2):
            raise pm.ModelException('Ball flew out of the tube')

    def calc_output(self, input_vector):
        """
        return ball position as output
        :param input_vector: input values
        :return: ball position
        """
        return input_vector[2]

pm.register_simulation_module(pm.Model, BallInTubeModel)
pm.register_simulation_module(pm.Model, BallInTubeSpringModel)
