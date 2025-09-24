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
beam_width = 0.2  # m
beam_depth = 0.4  # m
beam_length = 9  # m

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

# -----------------------------------------------
# export settings latex-style
# -----------------------------------------------
latex_font_size = 14
label_size = 1 * latex_font_size
title_size = 1.5 * latex_font_size

# -----------------------------------------------
# color-settings for diagramms with more than
# one controller
# -----------------------------------------------
color_cycle = {'FController': 'royalblue',
               'GController': 'indianred',
               'JController': 'mediumorchid',
               'LSSController': 'limegreen',
               'PIFeedbackController': 'darkorange',
               }

# -----------------------------------------------
# TestCase A1 - Pole Variation
# -----------------------------------------------
paramPoleVariation = {
    'FController': {
        'pole_limits': [0, -3.5],
        'pole_step': 0.1,
    },
    'GController': {
        'pole_limits': [0, -3.3],
        'pole_step': 0.1,
    },
    # J FAILS
    'JController': {
        'pole_limits': [0, -4],
        'pole_step': 0.1,
    },
    'LSSController': {
        'pole_limits': [0, -3.9],
        'pole_step': 0.1,
    },
    'PIFeedbackController': {
        'pole_limits': [0, -4],
        'pole_step': 0.1,
    },
}

# -----------------------------------------------
# TestCase A - Step and other Responses
# -----------------------------------------------

# best konwon poles - gained in A1
# JController is for a step for all tested poles unstable!!!!!
# To give the JController a chance it is tested for poles [-0.5, ca. 0.1, -15]
# on the SmoothTransitionTrajectory (Position:[0,3], delta t:5)
poles = {'FController': -3.1,
         'GController': -2.8,
         'JController': -2.0,
         # -2.0 hauser standard
         'LSSController': -3.4,
         'PIFeedbackController': -3.7,
         }

# -----------------------------------------------
# TestCase B - parameter variation
# -----------------------------------------------
# parameter variation list
paramVariationListB = ['M', 'Jb']
paramToleranceList = [0.2, 0.3]

# parameter stability limits for best known poles
paramStabilityLimits = {
    'FController': {
        'M': [0.01, 1.0],
        'Jb': [0, 10e-6],
    },
    'GController': {
        'M': [0.01, 1],
        'Jb': [0, 10e-6],
    },
    # J FAILS
    'JController': {
        'M': [0.05, 10],
        'Jb': [0, 10e-6],
    },
    'LSSController': {
        'M': [0.01, 1],
        'Jb': [0, 10e-6],
    },
    'PIFeedbackController': {
        'M': [0.01, 1],
        'Jb': [0, 10e-6],
    },
}

# -----------------------------------------------
# TestCase C1 - parameter variation
# -----------------------------------------------
# parameter stability limits (plus a little bit)
# for sigma and delay for best known poles
paramStabilityLimitsSigmaDelay = {
    'FController': {
        'sigma': [0, 0.45],
        'sigma_step': 0.01,
        'delay': [0, 85],
        'delay_step': 5,
        },
    'GController': {
        'sigma': [0, 0.35],
        'sigma_step': 0.01,
        'delay': [0, 85],
        'delay_step': 5,
        },
    # J FAILS
    'JController': {
        'sigma': [0, 0],
        'sigma_step': 0.1,
        'delay': [0, 0],
        'delay_step': 1,
        },
    'LSSController': {
        'sigma': [0, 1],
        'sigma_step': 0.05,
        'delay': [0, 4],
        'delay_step': 1,
        },
    'PIFeedbackController': {
        'sigma': [0, 0.45],
        'sigma_step': 0.01,
        'delay': [0, 8],
        'delay_step': 1,
        },
    }

# -----------------------------------------------
# TestCase C2 - Limiter Variation
# -----------------------------------------------
smoothPoles = {'FController': -2.0,
               'GController': -2.0,
               'JController': -2.0,
               'LSSController': -3.4,
               'PIFeedbackController': -1.7,
               }
paramVariationDictC2 = {'limiter': {'lower_bound': round(M * G * 4.5, 1),
                                    'upper_bound': 3,
                                    'step_size': 0.1,
                                    }}
