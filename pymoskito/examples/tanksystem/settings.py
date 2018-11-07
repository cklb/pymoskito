# -*- coding: utf-8 -*-
import numpy as np
# -----------------------------------------------------------------------------
# global default settings for physical simulation
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# parameters of the tank system according to the
# real test station on the Institute of Automation and Control Engineeringat the
# Umit

Ku = 1.932928975455609e-05   # m**3 / (s V) - gain of pump
uA0 = 6.3                    # V - start voltage for the pump

rT1 = 0.060195545420039      # m - radius of tank 1
rT2 = 0.060195545420039      # m - radius of tank 2
rS1 = 0.004065038180786      # m - radius between drain and tank 1 by 1 rotation
rS2 = 0.003308239534353      # m - radius between drain and tank 2 by 2 rotation
g = 9.81                     # m / s^2 - gravity

AT1 = np.pi * rT1 ** 2       # m**2 - Tank 1 cross section
AT2 = np.pi * rT2 ** 2       # m**2 - Tank 2 cross section
AS1 = np.pi * rS1 ** 2       # m**2 - Outlet cross section Tank 1
AS2 = np.pi * rS2 ** 2       # m**2 - Outlet cross section Tank 2

hT1 = 0.3                    # m - height Tank 1
hT2 = 0.3                    # m - height Tank 2

scale = 2                    # scale for visualization

# -----------------------------------------------------------------------------
# export settings latex-style
# -----------------------------------------------------------------------------
latex_font_size = 14
label_size = 1*latex_font_size
title_size = 1.5*latex_font_size
