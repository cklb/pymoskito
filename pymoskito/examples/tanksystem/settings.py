# -*- coding: utf-8 -*-
import numpy as np
# -----------------------------------------------------------------------------
# global default settings for physical simulation
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# parameters of the tank system according to the
# real test station on the Institute of Automation and Control Engineeringat the
# Umit

Ku = 1.932928975455609e-05  # m**3 / (s V) - gain of pump
uA0 = 6.3                   # V - start voltage for the pump

rT = 0.060195545420039      # m - radius of tank
rS = 0.004065038180786      # m - radius between drain and tank by 1 rotation
g = 9.81                    # m / s^2 - gravity
hV = 0.065                  # m - distance between zero and valve

AT = np.pi * rT ** 2        # m**2 - Tankquerschnitt
AS = np.pi * rS ** 2        # m**2 - Abflussquerschnitt Tank

hT = 0.3                    # m - height Tank

scale = 2                   # Skalierung für die Visualisierung

# -----------------------------------------------------------------------------
# export settings latex-style
# -----------------------------------------------------------------------------
latex_font_size = 14
label_size = 1*latex_font_size
title_size = 1.5*latex_font_size
