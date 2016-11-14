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

# class Feedforward(pm.Feedforward):
#
#     def __init__(self, order):
#         SimulationModule.__init__(self)
#         self.order = order
#         return
#
#     def getOrder(self):
#         return self.order
#
#     def getOutputDimension(self):
#         return 1
#
#     def setStepWidth(self, width):
#         self.step_width = width
#
#     def feed(self, yd):
#         u = self.calcOutput(yd)
#         return u


# class ApproximateFeedforward(pm.Feedforward):
#     """
#     Feedforward that is based on an approximated system
#     """
#
#     public_settings = OrderedDict([("M", st.M),
#                                    ("R", st.R),
#                                    ("J", st.J),
#                                    ("Jb", st.Jb),
#                                    ("G", st.G),
#                                    ("beam length", st.beam_length),
#                                    ("beam width", st.beam_width),
#                                    ("beam depth", st.beam_depth),
#                                    ("tick_divider", 1)])
#
#     def __init__(self, settings):
#         # add specific "private" settings
#         settings.update(input_order=2)
#         settings.update(output_dim=1)
#
#         pm.Feedforward.__init__(self, settings)
#
#     def calc_theta_t(self, rdd):
#         return (-1 / (self._settings["M"] * self._settings["G"])
#                 * (self._settings["Jb"] / self._settings["R"] ** 2
#                    + self._settings["M"]) * rdd)
#
#     def _feedforward(self, yd, **kwargs):
#         theta = []
#         for i in range(self._settings["input_order"] + 1):
#             theta.append(self._calc_theta_t(yd[i + 2]))
#
#         tau = ((self.settings['J'] + self.settings['Jb']) * theta[2]
#                + self.settings['M'] * self.settings['G'] * yd[0])
#
#         return tau


# class TighterApproximateFeedforward(Feedforward):
#     '''
#     Calculation of tau is more precise than in the ApproximateFeedforward
#     '''
#
#     settings = {'M': st.M, \
#                 'R': st.R, \
#                 'J': st.J, \
#                 'Jb': st.Jb, \
#                 'G': st.G, \
#                 'beam length': st.beam_length, \
#                 'beam width': st.beam_width, \
#                 'beam depth': st.beam_depth, \
#                 }
#
#     derOrder = 2
#
#     def __init__(self):
#         Feedforward.__init__(self, 2 + self.derOrder)
#         self.theta_t = lambda rdd: -1 / (
#         self.settings['M'] * self.settings['G']) \
#                                    * (
#                                    self.settings['Jb'] / self.settings['R'] ** 2 \
#                                    + self.settings['M']) * rdd
#
#     def calcOutput(self, yd):
#         tau = 0
#         theta = []
#         for i in range(self.derOrder + 1):
#             theta.append(self.theta_t(yd[i + 2]))
#
#         tau = (self.settings['M'] * yd[0] ** 2 + self.settings['J'] \
#                + self.settings['Jb']) * theta[2] \
#               + 2 * self.settings['M'] * yd[0] * yd[1] * theta[1] \
#               + self.settings['M'] * self.settings['G'] * yd[0] * np.cos(
#             theta[0])
#
#         return float(tau)
#
#
# class ExactFeedforward(Feedforward):
#     '''
#     Calculation of tau is nearly exact
#     '''
#
#     settings = {'M': st.M, \
#                 'R': st.R, \
#                 'J': st.J, \
#                 'Jb': st.Jb, \
#                 'G': st.G, \
#                 'beam length': st.beam_length, \
#                 'beam width': st.beam_width, \
#                 'beam depth': st.beam_depth, \
#                 }
#     derOrder = 3
#
#     def __init__(self):
#         Feedforward.__init__(self, self.derOrder)
#         self.firstRun = True
#
#     def calcOutput(self, yd):
#         if self.firstRun == True:
#             r, r_d, r_dd, r_ddd, theta = sp.symbols(
#                 'r, r_d, r_dd, r_ddd, theta')
#             theta_d = sp.sqrt((self.settings['Jb'] / self.settings['R'] ** 2 \
#                                + self.settings['M']) * r_dd \
#                               / (self.settings['M'] * r) \
#                               + self.settings['G'] * sp.sin(theta) / r)
#
#             theta_dd = (((self.settings['Jb'] / self.settings['R'] ** 2 \
#                           + self.settings['M']) * r_ddd \
#                          / (self.settings['M'] * r)) \
#                         - ((self.settings['Jb'] / self.settings['R'] ** 2 \
#                             + self.settings['M']) * r_d * r_dd \
#                            / (self.settings['M'] * r ** 2)) \
#                         + (self.settings['G'] * sp.cos(theta) * theta_d / r) \
#                         - (self.settings['G'] * sp.sin(theta) * r_d / r ** 2)) \
#                        / (2 * theta_d)
#
#             self.theta_d_func = sp.lambdify((r, r_dd, theta), theta_d,
#                                             modules='math')
#             self.theta_dd_func = sp.lambdify((r, r_d, r_dd, r_ddd, theta),
#                                              theta_dd, modules='math')
#
#             # TODO: what is the initial value of theta
#             self.next_theta = float(0)
#
#             self.firstRun = False
#
#         self.theta = self.next_theta
#
#         dt = self.step_width
#         try:
#             theta_d = self.theta_d_func(yd[0], yd[2], self.theta)
#             theta_dd = self.theta_dd_func(yd[0], yd[1], yd[2], yd[3],
#                                           self.theta)
#         except ZeroDivisionError:
#             # print 'zero division'
#             theta_d = 0
#             theta_dd = 0
#         except ValueError:
#             # print 'ValueError (because of a negative sqrt)'
#             theta_d = 0
#             theta_dd = 0
#
#         # EULER integration
#         self.next_theta = self.theta + dt * theta_d
#
#         # calculate tau
#         tau = (self.settings['M'] * yd[0] ** 2 + self.settings['J'] \
#                + self.settings['Jb']) * theta_dd \
#               + 2 * self.settings['M'] * yd[0] * yd[1] * theta_d \
#               + self.settings['M'] * self.settings['G'] * yd[0] * np.cos(
#             self.theta)
#
#         #        print tau
#         #        print self.theta
#         #        print theta_d
#         #        print theta_dd
#         #        print '--------------------------------------------'
#
#         return tau


pm.register_simulation_module(pm.Feedforward, LinearFeedforward)
