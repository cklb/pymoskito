"""
globally stored settings for the balance board system

all values taken from 
"R. Räbiger - Weiterentwicklung eines Versuchsstandes zur Regelung des Balance-Brett-Systems"
TU Dresden, SA 2013
"""
# ------------settings for model------------

g   = 9.81      # gravity [m/s^2]

# board
m1  = 1.2723    # mass [kg]
xS1 = -2e-3     # centre of gravity x-direction[m]
yS1 = 41.4e-3   # centre of gravity y-direction[m]
I1  = 4.56e-2   # moment of inertia [kg*m^2]
L1  = .6        # length [m]
# carriage
m2  = .1932     # mass [kg]
yS2 = 72e-3     # centre of gravity y-direction[m]
I2  = 2.06e-4   # moment of inertia [kg*m^2]
# cylinder
m3  = 3.9901    # mass [kg]
yS3 = -0.9e-3   # centre of gravity: distance to centre of area[m]
r   = 66e-3     # radius [m]
I3  = 8.71e-3   # moment of inertia [kg*m^2]

# constants of damping
cB  = 2.26e-2   # board <-> cylinder [kg*m^2/s]
cZ  = 3.69e-3   # ground <-> cylinder [kg*m^2/s]
cG  = 0.01      # ground <-> board [%]

init = [0,0,0,0,0,0]


# ------------settings for visualization------------

x_min_plot = -1
x_max_plot =  1
y_min_plot = -.5
y_max_plot =  .5

visBoardLength = L1
visBoardWidth  = .02
visBoardDepth  = .094

visMassLength = .1
visMassWidth  = .05
visMassDepth  = .06