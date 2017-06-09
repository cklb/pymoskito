# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# global default settings for physical simulation
# ---------------------------------------------------------------------

# standard values for integration
step_size = 0.002
measure_rate = 500

# initial minimal state vector (n, dn, x, dx)
# default values (used if none is given)
initial_state = [0, 0, 180, 0, 180, 0]

# system values and parameters fo the two pendulum system
g = 9.81                  # m/s**2
# cart:
m0_star = 4.0262          # kg
d0 = 10                   # Ns/m

# long pendulum:
m1_star = 0.3239          # kg
l1_star = 0.446265876476  # m
# d1 = 0.023              # Nms (amira)
d1 = 0.0018468868         # Nms
fv1 = 1.523e-3            # Nms
fc1 = 2.004e-3            # Nm
fh1 = 4.017e-3            # Nm

# short pendulum
m2_star = 0.2357          # kg
l2_star = 0.132090816395  # m
# d2 = 0.00145            # Nms (amira)
d2 = 0.001058521          # Nms
fv2 = 5.974e-9            # Nms
fc2 = 7.717e-3            # Nm
fh2 = 5.451e-3            # Nm

J_DP1 = 0.0723726153903   # kg*m**2
J_DP2 = 0.00428652915258  # kg*m**2
J1_MP = J_DP1 - m1_star*l1_star**2
J2_MP = J_DP2 - m2_star*l2_star**2

# transform the mass and length of the original system in to a
# mass and length of a point-mass-system
l1 = J_DP1/(m1_star*l1_star)
l2 = J_DP2/(m2_star*l2_star)

m1 = (m1_star*l1_star)**2/J_DP1
m2 = (m2_star*l2_star)**2/J_DP2

m0 = m0_star + (m1_star - m1) + (m2_star - m2)

# print m0_star, m0, d0
# print m1_star, m1, l1_star, l1, J_DP1, d1
# print m2_star, m2, l2_star, l2, J_DP2, d2

# information in mm

# beam parameter
beam_length = 1575/1000
beam_height = 10 / 1000
beam_depth = 150/1000

# cart parameter
cart_length = 145/1000
cart_height = 60 / 1000
cart_depth = 135/1000

axis_height = 47.5/1000
axis_radius = (11.8/1000)/2

pendulum_shaft_height = 27/1000
pendulum_shaft_radius = (40/1000)/2

pendulum_weight_height = 40/1000
pendulum_weight_radius = (30/1000)/2

short_pendulum_height = 100/1000 + pendulum_shaft_radius
short_pendulum_radius = (10/1000)/2

long_pendulum_height = 500/1000 + pendulum_shaft_radius
long_pendulum_radius = (10/1000)/2

# xlim for mpl plot
x_min_plot = -850/1000
x_max_plot = 850/1000

y_min_plot = -600/1000
y_max_plot = 600/1000
