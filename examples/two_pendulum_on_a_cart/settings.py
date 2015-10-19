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
initial_state = [0, 0, 0, 0, 0, 0]
int_mode = 'vode'
int_method = 'adams'
int_rtol = 1e-6
int_atol = 1e-9
end_time = 20

# system values and parameters fo the two pendulum system
g = 9.81                # m/s**2
# cart:
m0_real = 4.2774        # kg
d0 = -10                # Ns/m
# long pendulum:
m1_real = 0.3211        # kg
a1 = 0.3533             # m
J1_real = 0.072         # kgm**2
d1 = -0.023             # Ns
# short pendulum
m2_real = 0.2355        # kg
a2 = 0.0963             # m
J2_real = 0.0044        # kgm**2
d2 = -0.00145           # Ns

# transform the mass and length of the original system in to a
# mass and length of a point-mass-system
l1 = J1_real/(m1_real*a1)
l2 = J2_real/(m2_real*a2)

m1 = (m1_real*a1)**2/J1_real
m2 = (m2_real*a2)**2/J2_real

m0 = m0_real + (m1_real - m1) + (m2_real - m2)

# beam parameter
beam_length = 1.575     # m
beam_width = 0.01       # m
beam_depth = 0.15       # m

# information in mm

# cart parameter
cart_length = 145/1000
cart_width = 60/1000
cart_depth = 135/1000

axis_height = 47.5/1000
axis_radius = (11.8/1000)/2

pendulum_shaft_height = 27/1000
pendulum_shaft_radius = (40/1000)/2

pendulum_weight_height = 40/1000
pendulum_weight_radius = (30/1000)/2

short_pendulum_height = 100/1000 + pendulum_shaft_radius
short_pendulum_radius = (10/1000)/2