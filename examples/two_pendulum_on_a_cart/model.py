__author__ = 'stefan'

from collections import OrderedDict
import numpy as np
import pymoskito.pymoskito as pm
from pymoskito.simulation_modules import Model, ModelException

import settings as st


class TwoPendulumModel(Model):
    """
    Implementation of the two pendulum on a cart system
    """
    public_settings = OrderedDict([('initial state', st.initial_state),
                                   ("m0", st.m0_real),
                                   ("d0", st.d0),
                                   ("m1", st.m1_real),
                                   ("a1", st.a1),
                                   ("J1", st.J1_real),
                                   ("d1", st.d1),
                                   ("m2", st.m2_real),
                                   ("a2", st.a2),
                                   ("J2", st.J2_real),
                                   ("d2", st.d2),
                                   ("g", st.g),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        Model.__init__(self, settings)

        # shortcuts for readability
        self.d0 = self._settings['d0']
        self.d1 = self._settings['d1']
        self.d2 = self._settings['d2']
        self.g = self._settings['g']

        self.l1 = self._settings['J1']/(self._settings['m1']*self._settings['a1'])
        self.l2 = self._settings['J2']/(self._settings['m2']*self._settings['a2'])

        self.m1 = (self._settings['m1']*self._settings['a1'])**2/self._settings['J1']
        self.m2 = (self._settings['m2']*self._settings['a2'])**2/self._settings['J2']

        self.m0 = self._settings['m0'] + (self._settings['m1'] - self.m1) + (self._settings['m2'] - self.m2)

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
        u = (F1
             + F2
             + (F_star - self.d0*x2)
             + (M1_star - self.d1*x4)*np.cos(x3)/self.l1
             + (M2_star - self.d2*x6)*np.cos(x5)/self.l2)/M

        dx1 = x2
        dx2 = u
        dx3 = x4
        dx4 = self.g*np.sin(x3)/self.l1 + u*np.cos(x3)/self.l1 + (M1_star - self.d1*x4)/(self.m1*self.l1**2)
        dx5 = x6
        dx6 = self.g*np.sin(x5)/self.l2 + u*np.cos(x5)/self.l2 + (M2_star - self.d2*x6)/(self.m2*self.l2**2)

        dx = np.array([[dx1],
                       [dx2],
                       [dx3],
                       [dx4],
                       [dx5],
                       [dx6]])
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
        return np.array([input[0]], dtype=float)

    def f(self, x, u):
        from sympy import cos, sin
        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        x5 = x[4]
        x6 = x[5]
        u, = u
        M1_star = 0
        M2_star = 0

        # transformation of the input
        M = self.m0 + self.m1*(sin(x3))**2 + self.m2*(sin(x5))**2
        F1 = self.m1*sin(x3)*(self.g*cos(x3) - self.l1*x4**2)
        F2 = self.m2*sin(x5)*(self.g*cos(x5) - self.l2*x6**2)
        uu = (F1
             + F2
             + (u - self.d0*x2)
             + (M1_star - self.d1*x4)*cos(x3)/self.l1
             + (M2_star - self.d2*x6)*cos(x5)/self.l2)/M

        dx1 = x2
        dx2 = uu
        dx3 = x4
        dx4 = self.g*sin(x3)/self.l1 + uu*cos(x3)/self.l1 + (M1_star - self.d1*x4)/(self.m1*self.l1**2)
        dx5 = x6
        dx6 = self.g*sin(x5)/self.l2 + uu*cos(x5)/self.l2 + (M2_star - self.d2*x6)/(self.m2*self.l2**2)

        ff = np.array([dx1,
                       dx2,
                       dx3,
                       dx4,
                       dx5,
                       dx6])
        return ff


class TwoPendulumModel2(Model):
    """
    Implementation of the two pendulum on a cart system
    """
    public_settings = OrderedDict([('initial state', [0, 0, 0.1, 0, 0, 0]),
                                   ("m0", st.m0_real),
                                   ("d0", st.d0),
                                   ("m1", st.m1_real),
                                   ("a1", st.a1),
                                   ("J1", st.J1_real),
                                   ("d1", st.d1),
                                   ("m2", st.m2_real),
                                   ("a2", st.a2),
                                   ("J2", st.J2_real),
                                   ("d2", st.d2),
                                   ("g", st.g),
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        Model.__init__(self, settings)

        print self._settings
        # shortcuts for readability
        self.d0 = self._settings['d0']
        self.d1 = self._settings['d1']
        self.d2 = self._settings['d2']
        self.g = self._settings['g']

        self.a1 = self._settings['a1']
        self.a2 = self._settings['a2']

        self.J1 = self._settings['J1']
        self.J2 = self._settings['J2']

        self.m0 = st.m0_real
        self.m1 = st.m1_real
        self.m2 = st.m2_real

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
        term1 = self.m0 + self.m1 + self.m2 - self.m1**2*self.a1**2*(np.cos(x3))**2/self.J1 \
                - self.m2**2*self.a2**2*(np.cos(x5))**2/self.J2
        term2 = self.m1*self.a1*(np.cos(x3))*(M1 - self.d1*x4 + self.m1*self.a1*self.g*np.sin(x3))/self.J1
        term3 = self.m2*self.a2*(np.cos(x5))*(M2 - self.d2*x6 + self.m2*self.a2*self.g*np.sin(x5))/self.J2
        term4 = F - self.d0*x2 - self.m1*self.a1*x4**2*np.sin(x3) - self.m2*self.a2*x6**2*np.sin(x5)

        dx1 = x2
        dx2 = (term2 + term3 + term4)/term1
        dx3 = x4
        dx4 = (self.m1*self.a1*np.cos(x3)*dx2 + M1 - self.d1*x4 + self.m1*self.a1*self.g*np.sin(x3))/self.J1
        dx5 = x6
        dx6 = (self.m2*self.a2*np.cos(x5)*dx2 + M2 - self.d2*x6 + self.m2*self.a2*self.g*np.sin(x5))/self.J2

        dx = np.array([[dx1],
                       [dx2],
                       [dx3],
                       [dx4],
                       [dx5],
                       [dx6]])
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
        return np.array([input[0]], dtype=float)


pm.register_simulation_module(Model, TwoPendulumModel)
pm.register_simulation_module(Model, TwoPendulumModel2)
