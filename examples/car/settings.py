# -*- coding: utf-8 -*-

from __future__ import division

# ---------------------------------------------------------------------
# global default settings for physical simulation
# ---------------------------------------------------------------------

# standard values for integration
step_size = 0.0005
measure_rate = 1000

# initial minimal state vector (n, dn, x, dx) default values (used if none is given)
initial_state = [0, 0, 0, 0, 0]
int_mode = 'vode'
int_method = 'adams'
int_rtol = 1e-6
int_atol = 1e-9
end_time = 10

# system parameters
d1 = 0.08
l2 = 0.19
d2 = 0.08
l3 = 0.19

# animation parameters
dia = 0.1
car_radius = dia/2
wheel = dia/4
