# -*- coding: utf-8 -*-
import numpy as np

# system values and parameters of the rod pendulum

# standard values for integration
step_size = 0.001
measure_rate = 500.0

# initial state vector (s, phi, ds/dt, dphi/dt)
# default values (used if none is given)
initial_state = [0, 180.0, 0, 0]
int_mode = 'vode'
int_method = 'adams'
int_rtol = 1e-6
int_atol = 1e-9
end_time = 20.0


# pendulum
m1 = 358.3 / 1000.0  # kg
l1 = 1.01  # m
a1 = 0.43  # m --> determined by experiments
# the brassy part and the screw at the end of the rod was not regarded
J1 = 0.0379999429  # Nms**2
d1 = 0.0058885212  # Nms
r_stab = 6.0 / 1000.0  # m radius of the rod

# cart and motor
m0 = 3.340  # kg - weight of the cart
kM = 0.4255  # Nm/A - torque constant/motor constant
U = 70.0 / 1000.0  # m - perimeter/covered distance per turn
r = U / (2.0 * np.pi)  # m

g = 9.81  # m/s**2 - gravity

# parameter for the visualisation, all information in mm

# beam parameter
beam_length = 2543.0/1000.0
beam_height = 5.0 / 1000.0
beam_depth = 90.0 / 1000.0

# cart parameter
cart_length = 195.0/1000.0
cart_height = 60.0 / 1000.0
cart_depth = 135.0/1000.0

axis_height = 47.5/1000.0
axis_radius = (11.8/1000.0)/2.0

pendulum_shaft_height = 27.0/1000.0
pendulum_shaft_radius = (40.0/1000.0)/2.0

rod_pendulum_height = 1010.0/1000.0 + pendulum_shaft_radius
rod_pendulum_radius = (12.0/1000.0)/2.0

# xlim for mpl plot
x_min_plot = -1300.0/1000.0
x_max_plot = 1300.0/1000.0

# ylim for mpl plot
y_min_plot = -1100.0/1000.0
y_max_plot = 1100.0/1000.0

