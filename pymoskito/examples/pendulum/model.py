# -*- coding: utf-8 -*-
from collections import OrderedDict
import numpy as np

import pymoskito as pm

from . import settings as st


class TwoPendulumModel(pm.Model):
    """
    Implementation of the two pendulum on a cart system
    this is implemented as a point mass model
    """
    public_settings = OrderedDict([("initial state", st.initial_state),
                                   ("m0*", st.m0_star),
                                   ("d0", st.d0),
                                   ("m1*", st.m1_star),
                                   ("l1*", st.l1_star),
                                   ("J_DP1", st.J_DP1),
                                   ("d1", st.d1),
                                   ("m2*", st.m2_star),
                                   ("l2*", st.l2_star),
                                   ("J_DP2", st.J_DP2),
                                   ("d2", st.d2),
                                   ("g", st.g),
                                   ])

    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][2:] = [
            val*np.pi/180.0 for val in settings["initial state"][2:]]

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "cart-position", "Unit": "m"},
            1: {"Name": "cart-velocity", "Unit": "m"},
            2: {"Name": "long-pendulum-angle", "Unit": "rad/s"},
            3: {"Name": "long-pendulum-angular-velocity", "Unit": "rad/s"},
            4: {"Name": "short-pendulum-angle", "Unit": "rad"},
            5: {"Name": "short-pendulum-angular-velocity", "Unit": "rad/s"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.d0 = self._settings["d0"]
        self.d1 = self._settings["d1"]
        self.d2 = self._settings["d2"]
        self.g = self._settings["g"]

        self.l1 = self._settings["J_DP1"]/(self._settings["m1*"]*self._settings["l1*"])
        self.l2 = self._settings["J_DP2"]/(self._settings["m2*"]*self._settings["l2*"])

        self.m1 = (self._settings["m1*"]*self._settings["l1*"])**2/self._settings["J_DP1"]
        self.m2 = (self._settings["m2*"]*self._settings["l2*"])**2/self._settings["J_DP2"]

        self.m0 = self._settings["m0*"] + (self._settings["m1*"] - self.m1) + (self._settings["m2*"] - self.m2)

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        x5 = x[4]
        x6 = x[5]
        F_star = args[0]
        M1_star = 0
        M2_star = 0

        # transformation of the input
        M = self.m0 + self.m1*(np.sin(x3))**2 + self.m2*(np.sin(x5))**2
        F1 = self.m1*np.sin(x3)*(self.g*np.cos(x3) - self.l1*x4**2)
        F2 = self.m2*np.sin(x5)*(self.g*np.cos(x5) - self.l2*x6**2)
        u = (F1 +
             F2 +
             (F_star - self.d0*x2) +
             (M1_star - self.d1*x4)*np.cos(x3)/self.l1 +
             (M2_star - self.d2*x6)*np.cos(x5)/self.l2)/M

        dx1 = x2
        dx2 = u
        dx3 = x4
        dx4 = self.g*np.sin(x3)/self.l1 + u*np.cos(x3)/self.l1 + (M1_star - self.d1*x4)/(self.m1*self.l1**2)
        dx5 = x6
        dx6 = self.g*np.sin(x5)/self.l2 + u*np.cos(x5)/self.l2 + (M2_star - self.d2*x6)/(self.m2*self.l2**2)

        dx = np.array([dx1, dx2, dx3, dx4, dx5, dx6])
        return dx

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        """
        Check something
        """
        pass

    def calc_output(self, input):
        """
        return cart position as output
        :param input: input values
        :return: cart position
        """
        return input[0]


class TwoPendulumRigidBodyModel(pm.Model):
    """
    Implementation of the two pendulum on a cart system
    this is implemented as rigid body model
    """
    public_settings = OrderedDict([("initial state", st.initial_state),
                                   ("m0*", st.m0_star),
                                   ("d0", st.d0),
                                   ("m1*", st.m1_star),
                                   ("l1*", st.l1_star),
                                   ("J_DP1", st.J_DP1),
                                   ("d1", st.d1),
                                   ("m2*", st.m2_star),
                                   ("l2*", st.l2_star),
                                   ("J_DP2", st.J_DP2),
                                   ("d2", st.d2),
                                   ("g", st.g),
                                   ])

    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][2:] = settings["initial state"][2:]*np.pi/180
        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "cart-position", "Unit": "m"},
            1: {"Name": "cart-velocity", "Unit": "m"},
            2: {"Name": "long-pendulum-angle", "Unit": "rad/s"},
            3: {"Name": "long-pendulum-angular-velocity", "Unit": "rad/s"},
            4: {"Name": "short-pendulum-angle", "Unit": "rad"},
            5: {"Name": "short-pendulum-angular-velocity", "Unit": "rad/s"},
        }})
        pm.Model.__init__(self, settings)

        print(self._settings)
        # shortcuts for readability
        self.d0 = self._settings["d0"]
        self.d1 = self._settings["d1"]
        self.d2 = self._settings["d2"]
        self.g = self._settings["g"]

        self.l1_star = self._settings["l1*"]
        self.l2_star = self._settings["l2*"]

        self.J_DP1 = self._settings["J_DP1"]
        self.J_DP2 = self._settings["J_DP2"]

        self.m0_star = self._settings["m0*"]
        self.m1_star = self._settings["m1*"]
        self.m2_star = self._settings["m2*"]

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        x5 = x[4]
        x6 = x[5]
        F = args[0]
        M1 = 0
        M2 = 0

        # transformation of the input
        term1 = (self.m0_star
                 + self.m1_star
                 + self.m2_star
                 - self.m1_star**2*self.l1_star**2*(np.cos(x3))**2/self.J_DP1
                 - self.m2_star**2*self.l2_star**2*(np.cos(x5))**2/self.J_DP2)
        term2 = self.m1_star*self.l1_star*(np.cos(x3))*(M1
                                                        - self.d1*x4
                                                        + self.m1_star*self.l1_star*self.g*np.sin(x3))/self.J_DP1
        term3 = self.m2_star*self.l2_star*(np.cos(x5))*(M2
                                                        - self.d2*x6
                                                        + self.m2_star*self.l2_star*self.g*np.sin(x5))/self.J_DP2
        term4 = (F
                 - self.d0*x2
                 - self.m1_star*self.l1_star*x4**2*np.sin(x3)
                 - self.m2_star*self.l2_star*x6**2*np.sin(x5))

        dx1 = x2
        dx2 = (term2 + term3 + term4)/term1
        dx3 = x4
        dx4 = (self.m1_star*self.l1_star*np.cos(x3)*dx2
               + M1
               - self.d1*x4
               + self.m1_star*self.l1_star*self.g*np.sin(x3))/self.J_DP1
        dx5 = x6
        dx6 = (self.m2_star*self.l2_star*np.cos(x5)*dx2
               + M2
               - self.d2*x6
               + self.m2_star*self.l2_star*self.g*np.sin(x5))/self.J_DP2

        dx = np.array([dx1, dx2, dx3, dx4, dx5, dx6])
        return dx

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        """
        Check something
        """
        pass

    def calc_output(self, input):
        """
        return cart position as output
        :param input: input values
        :return: cart position
        """
        return input[0]


class TwoPendulumModelParLin(pm.Model):
    """
    Implementation of the two pendulum on a cart system, with a acceleration as input
    this is the partial linerarisation of the TwoPendulumModel
    """
    public_settings = OrderedDict([("initial state", st.initial_state),
                                   ("m0*", st.m0_star),
                                   ("d0", st.d0),
                                   ("m1*", st.m1_star),
                                   ("l1*", st.l1_star),
                                   ("J_DP1", st.J_DP1),
                                   ("d1", st.d1),
                                   ("m2*", st.m2_star),
                                   ("l2*", st.l2_star),
                                   ("J_DP2", st.J_DP2),
                                   ("d2", st.d2),
                                   ("g", st.g),
                                   ])

    def __init__(self, settings):
        # conversion from degree to radiant
        settings["initial state"][2:] = settings["initial state"][2:]*np.pi/180
        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "cart-position", "Unit": "m"},
            1: {"Name": "cart-velocity", "Unit": "m"},
            2: {"Name": "long-pendulum-angle", "Unit": "rad/s"},
            3: {"Name": "long-pendulum-angular-velocity", "Unit": "rad/s"},
            4: {"Name": "short-pendulum-angle", "Unit": "rad"},
            5: {"Name": "short-pendulum-angular-velocity", "Unit": "rad/s"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability
        self.d0 = self._settings["d0"]
        self.d1 = self._settings["d1"]
        self.d2 = self._settings["d2"]
        self.g = self._settings["g"]

        self.l1 = self._settings["J_DP1"]/(self._settings["m1*"]*self._settings["l1*"])
        self.l2 = self._settings["J_DP2"]/(self._settings["m2*"]*self._settings["l2*"])

        self.m1 = (self._settings["m1*"]*self._settings["l1*"])**2/self._settings["J_DP1"]
        self.m2 = (self._settings["m2*"]*self._settings["l2*"])**2/self._settings["J_DP2"]

        self.m0 = self._settings["m0*"] + (self._settings["m1*"] - self.m1) + (self._settings["m2*"] - self.m2)

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input force on the cart
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        x5 = x[4]
        x6 = x[5]
        u = args[0][0]

        dx1 = x2
        dx2 = u
        dx3 = x4
        dx4 = self.g*np.sin(x3)/self.l1 - (self.d1*x4)/(self.m1*self.l1**2) + np.cos(x3)*u/self.l1
        dx5 = x6
        dx6 = self.g*np.sin(x5)/self.l2 - (self.d2*x6)/(self.m2*self.l2**2) + np.cos(x5)*u/self.l2

        dx = np.array([dx1, dx2, dx3, dx4, dx5, dx6])
        return dx

    def root_function(self, x):
        return [False]

    def check_consistency(self, x):
        """
        Check something
        """
        pass

    def calc_output(self, input):
        """
        return cart position as output
        :param input: input values
        :return: cart position
        """
        return input[0]

pm.register_simulation_module(pm.Model, TwoPendulumModel)
pm.register_simulation_module(pm.Model, TwoPendulumModelParLin)
pm.register_simulation_module(pm.Model, TwoPendulumRigidBodyModel)
