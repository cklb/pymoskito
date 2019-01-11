# -*- coding: utf-8 -*-

"""
This file contains default settings for physical simulation of the ball and beam
system. These values are used to maintain consistent settings over the whole
test system. The values given here are used to generate regime lists that are
used to perform experimental studies.
"""

# standard values for integration
step_size = 0.0005  # to produce same error dimension as hauser
measure_rate = 1000  # to produce same error dimension as hauser

# initial minimal state vector (r, dr, theta, dtheta)
# default values (used if none is given)
initial_state = [0, 0, 0, 0]

# integrator defaults
int_mode = "vode"
int_method = "adams"
int_rtol = 1e-6
int_atol = 1e-9
end_time = 20

# nominal system values
M = 0.05  # kg
R = 0.01  # m
J = 0.02  # kgm^2
Jb = 2e-6  # kgm^2
G = 9.81  # m/s^2
B = M / (Jb / R ** 2 + M)
beam_width = 0.1        # m
beam_depth = 9          # m
beam_length = 9         # m
Fachwerk_length = 10    # m
Offset = 0.05
Abstand_a = 0.8
Abstand_b = 0.2

# operating point
q_op = [0, 0, 0, 0]
tau_op = 0

# poles for LSSController
poles_LSSController = [-2, -2, -2, -2]

# poles for LuenbergerObserver
poles_LuenbergerObserver = [-3, -3, -3, -3]

# Visualization
ballScale = 30
visR = R * ballScale
visBeamWidth = beam_width
visBeamLength = beam_length
visBeamDepth = beam_depth

# mpl settings
x_min_plot = -.6 * visBeamLength
x_max_plot = .6 * visBeamLength
y_min_plot = -(visR + visBeamLength / 3 + visBeamWidth)
y_max_plot = visR + visBeamLength / 3


import numpy as np
A = np.array([[0, 1, 0, 0],
              [0, 0, 0, 0],
              [0, 0, 0, 1],
              [0, 0, 0, 0]])
B_1 = np.array([[0, 0],
                [0, G],
                [0, 0],
                [-G, 0]]) * 5 / 7
B_2 = np.array([[0, 0],
                [0, -Abstand_b],
                [0, 0],
                [(Abstand_a + Abstand_b), 0]]) * 5 / 7
# K = np.array([[0, 0, -1.14, -0.86],
#               [1.14, 0.86, 0, 0]])
K = np.array([[0, 0, -0.2854, -0.43],
              [0.2854, 0.43, 0, 0]])
Zustand = np.array([[0],
                    [0],
                    [0],
                    [0]])
L = np.array([[20, 0],
              [96, 0],
              [0, 20],
              [0, 96]])
C = np.array([[1, 0, 0, 0],
              [0, 0, 1, 0]])
T = np.array([[1.04, 0.03, 0, 0],
              [-0.03, 0.86, 0, 0],
              [0, 0, 1.04, 0.03],
              [0, 0, -0.03, 0.86]])
A_Ableitung = A-B_1@K
K_1 = np.array([[0, 0, -0.2854, -0.43]])
K_2 = np.array([[0.2854, 0.43, 0, 0]])