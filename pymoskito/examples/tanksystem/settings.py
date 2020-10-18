# -*- coding: utf-8 -*-
import numpy as np
# -----------------------------------------------------------------------------
# global default settings for physical simulation
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# parameters of the tank system according to the

K = 2e-5                     # m**3 / (s V) - gain of pump

rT = 0.04                    # m - radius of the tanks
g = 9.81                     # m / s^2 - gravity

AT = np.pi * rT ** 2         # m**2 - Tanks cross section
hT = 0.8                     # m - height of the tanks

rS1 = 0.0035                 # m - radius of pipe cross section between tank 1 and 2
rS2 = 0.0035                 # m - radius of pipe cross section after tank 2

AS1 = np.pi * rS1 ** 2       # m**2 - Outlet cross section of drain between tank 1 and 2
AS2 = np.pi * rS2 ** 2       # m**2 - Outlet cross section of drain of tank 2

# -----------------------------------------------------------------------------
# export settings latex-style
# -----------------------------------------------------------------------------
latex_font_size = 14
label_size = 1 * latex_font_size
title_size = 1.5 * latex_font_size
