# -*- coding: utf-8 -*-


# ---------------------------------------------------------------------
# global default settings for physical simulation
# ---------------------------------------------------------------------

# standard values for integration
step_size = 0.0005
measure_rate = 1000

# initial minimal state vector (n, dn, x, dx) default values (used if none is given)
initial_state = [0, 0, 180, 0, 180, 0]
int_mode = 'vode'
int_method = 'adams'
int_rtol = 1e-6
int_atol = 1e-9
end_time = 20

# system values and parameters fo the two pendulum system
g = 9.81                # m/s**2
# cart:
m0_star = 4.0262        # kg
d0 = 10                # Ns/m
# long pendulum:
m1_star = 0.3239       # kg
l1_star = 0.442698054955             # m
d1 = 0.023             # Ns
# short pendulum
m2_star = 0.2357        # kg
l2_star = 0.0952587218277             # m
d2 = 0.00145           # Ns

J_MP1 = m1_star*l1_star**2
J_MP2 = m2_star*l2_star**2
J_DP1 = J_MP1 + m1_star*l1_star**2
J_DP2 = J_MP2 + m2_star*l2_star**2

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
beam_width = 10/1000
beam_depth = 150/1000

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

long_pendulum_height = 500/1000 + pendulum_shaft_radius
long_pendulum_radius = (10/1000)/2