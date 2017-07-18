# -*- coding: utf-8 -*-
import numpy as np
# -----------------------------------------------------------------------------
# global default settings for physical simulation
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# parameters of the ball in tube system according to the
# real test station on the institute of control theory at the
# TU-Dresden

initial_state = [0, 0, 0, 0]

T = 0.24757155405           # s - time constant of the motor
d = 0.733277219979          # - damping ratio of the motor
k_s = 10.0291812304         # 1/Vs - gain motor
Vcc = 12                    # V - voltage supply

k_V = 6.28192637773e-05     # m**3 - factor between fan speed and airflow
k_L = 2.27269527471e-04     # N*s**2/m - factor between flow velocity in
#  the air gap squared and the buoyancy force
d_R = 64.4e-3               # m - diameter of the tube
d_R_out = 70.0e-3           # m - external diameter of the tube
tube_length = 1.5           # m -  length of the tube
d_B = 60.0e-3               # m - diameter of the ball
m = 2.8e-3                  # kg - mass of the ball
g = 9.81                    # m/s^2 - gravity

K = 10000                   # N/m - stiffness of the spring
D = 1                       # Ns/m - damping ratio of the spring

A_B = np.pi*d_B**2/4        # m**2 - cross sectional area of the ball
A_R = np.pi*d_R**2/4        # m**2 - cross sectional area of the tube
A_Sp = A_R - A_B            # m**2 - cross sectional area of air gap

scale = 2
visTubeLength = tube_length/scale
visTubeDiameter = d_R*scale
visBallDiameter = d_B*scale

# equilibrium
x1_e = A_Sp*np.sqrt(m*g/k_L)/k_V
x2_e = 0
x3_e = 0  # random
x4_e = 0
u_e = A_Sp*np.sqrt(m*g/k_L)/(k_V*k_s)

# -----------------------------------------------------------------------------
# export settings latex-style
# -----------------------------------------------------------------------------
latex_font_size = 14
label_size = 1*latex_font_size
title_size = 1.5*latex_font_size
