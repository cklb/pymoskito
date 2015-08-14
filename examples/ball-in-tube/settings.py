# -*- coding: utf-8 -*-

from __future__ import division

import numpy as np
# ---------------------------------------------------------------------
# global default settings for physical simulation
# ---------------------------------------------------------------------

# standard values for integration
step_size = 0.0005
measure_rate = 1000

# initial minimal state vector (n, dn, x, dx) default values (used if none is given)
initial_state = [0, 0, 0, 0]
int_mode = 'vode'
int_method = 'adams'
int_rtol = 1e-6
int_atol = 1e-9
end_time = 20

# # standard system values BallInTube
# d_B = 39.7e-3       # m
# d_n = 3.25          #
# d_p = 2.75          #
# d_R = 41e-3         # m
# k_L = 1.0637e-5     # N*s^2/m
# k_s = 7.04          # 1/V*s
# k_V = 8.3503e-5     # m^3
# m = 2.7122e-3       # kg
# T_n = 0.1950        # s
# T_p = 0.13          # s
tube_length = 1.5     # m

T_n = 0.27
T_p = 0.27
d_p = 0.81
d_n = 0.81
k_s = 10.1

k_V = 6.208e-5
k_L = 2.273e-4
d_R = 64.4e-3
d_B = 60.0e-3

g = 9.81            # m/s^2
m = 2.8e-3

A_B = np.pi*d_B**2/4
A_R = np.pi*d_R**2/4
A_Sp = A_R - A_B

scale = 2
visTubeLength = tube_length/scale
visTubeDiameter = d_R*scale
visBallDiameter = d_B*scale


# -----------------------------------------------
# export settings latex-style
# -----------------------------------------------
latex_font_size = 14
label_size = 1*latex_font_size
title_size = 1.5*latex_font_size
