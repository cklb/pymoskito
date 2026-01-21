# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 20:28:06 2014

Lagrange formalism

@author: Topher
"""

import sympy as sp
from sympy import sin,cos,Function

t = sp.Symbol('t')
params = sp.symbols('m1, x_{S1}, y_{S1}, I1, '
                    'm2, y_{S2}, I2, '
                    'm3, r, I3, c, '
                    'g')
m1, xS1, yS1, I1, m2, yS2, I2, m3, r, I3, c, g = params

# board deflection
psi_t = Function('psi')(t)
d_psi_t = psi_t.diff(t)
dd_psi_t = psi_t.diff(t,2)
# mass position
gamma_t = Function('gamma')(t)
d_gamma_t = gamma_t.diff(t)
dd_gamma_t = gamma_t.diff(t,2)
# board deflection
theta_t = Function('theta')(t)
d_theta_t = theta_t.diff(t)
dd_theta_t = theta_t.diff(t,2)

# force on mass
F = Function('F')
# friction board <-> cylinder
c = Function('c')


# kinetic energy
T = 0.5*( m1*(((r*psi_t + xS1 - r*theta_t)**2 + yS1**2)*d_psi_t**2 + 2*r**2*(1 + cos(psi_t))*d_theta_t**2
              + 2*r*((r*psi_t + xS1 - r*theta_t)*sin(psi_t) + yS1*(1 + cos(psi_t)))*d_psi_t*d_theta_t)
         + m2*(((r*psi_t + gamma_t - r*theta_t)**2 + yS2**2)*d_psi_t**2 + 2*r**2*(1 + cos(psi_t))*d_theta_t**2 + d_gamma_t**2
              + 2*r*((r*psi_t + gamma_t - r*theta_t)*sin(psi_t) + yS2*(1 + cos(psi_t)))*d_psi_t*d_theta_t
                - 2*yS2*d_gamma_t*d_psi_t - 2*r*(1 + cos(psi_t))*d_gamma_t*d_theta_t)
         + (I1 + I2)*d_psi_t**2 + (m3*r**2 + I3)*d_theta_t**2 )

# potential energy
V = g*(m1*((r + yS1)*cos(psi_t) + (r*psi_t + xS1 - r*theta_t)*sin(psi_t))
    + m2*((r + yS2)*cos(psi_t) + (r*psi_t + gamma_t - r*theta_t)*sin(psi_t)))

# lagrange function
L = T - V

# replace functions through symbols
psi_s , d_psi_s , dd_psi_s , gamma_s, d_gamma_s, dd_gamma_s, theta_s, d_theta_s , dd_theta_s = sp.symbols('psi_s , d_psi_s , dd_psi_s , gamma_s, d_gamma_s, dd_gamma_s, theta_s, d_theta_s , dd_theta_s')
subs_list = [(dd_psi_t,dd_psi_s),(dd_gamma_t,dd_gamma_s),(dd_theta_t,dd_theta_s),(d_psi_t,d_psi_s),(d_gamma_t,d_gamma_s),(d_theta_t,d_theta_s),(psi_t,psi_s),(gamma_t,gamma_s),(theta_t,theta_s)]
L = L.subs(subs_list)

# simplify L
L = L.expand()
L = sp.trigsimp(L)

# assitant terms
d_L_psi = L.diff(psi_s)
d_L_gamma = L.diff(gamma_s)
d_L_theta = L.diff(theta_s)

d_L_d_psi = L.diff(d_psi_s)
d_L_d_gamma = L.diff(d_gamma_s)
d_L_d_theta = L.diff(d_theta_s)

# replace symbols through functions
subs_list_rev = []
for tup in subs_list:
    subs_list_rev.append((tup[1],tup[0]))

#d_L_r = d_L_r.subs(subs_list_rev)
#d_L_theta = d_L_theta.subs(subs_list_rev)

d_L_d_psi = d_L_d_psi.subs(subs_list_rev)
d_L_d_gamma = d_L_d_gamma.subs(subs_list_rev)
d_L_d_theta = d_L_d_theta.subs(subs_list_rev)

# derivate to time
dt_d_L_d_psi = d_L_d_psi.diff(t)
dt_d_L_d_gamma = d_L_d_gamma.diff(t)
dt_d_L_d_theta = d_L_d_theta.diff(t)

# replace functions through symbols
dt_d_L_d_psi = dt_d_L_d_psi.subs(subs_list)
dt_d_L_d_gamma = dt_d_L_d_gamma.subs(subs_list)
dt_d_L_d_theta = dt_d_L_d_theta.subs(subs_list)

# lagrange equation
Eq_psi = dt_d_L_d_psi - d_L_psi
Eq_gamma = dt_d_L_d_gamma - d_L_gamma
Eq_theta = dt_d_L_d_theta - d_L_theta

#Eq_r = Eq_r.factor()
#Eq_theta = Eq_theta.factor()

Eq_psi = sp.Eq(0 , Eq_psi)
Eq_gamma = sp.Eq(F, Eq_gamma)
Eq_theta = sp.Eq(0, Eq_theta)

psi_s , d_psi_s , dd_psi_s , gamma_s , d_gamma_s , dd_gamma_s , theta_s, d_theta_s , dd_theta_s
# symbols in latex-notation
sn_dict = {psi_s: r'\Psi', d_psi_s: r'\dot{\Psi}', dd_psi_s: r'\ddot{\Psi}',
           gamma_s: r'\gamma', d_gamma_s: r'\dot{\gamma}', dd_gamma_s: r'\ddot{\gamma}',
           theta_s: r' \Theta', d_theta_s: r'\dot{\Theta}', dd_theta_s: r'\ddot{\Theta}'}

# show lagrange equation
import matplotlib.pyplot as plt
latex_str1 = "$ %s $" % sp.latex(Eq_psi,symbol_names = sn_dict)
latex_str2 = "$ %s $" % sp.latex(Eq_gamma,symbol_names = sn_dict)
latex_str3 = "$ %s $" % sp.latex(Eq_theta,symbol_names = sn_dict)
latex_str1 = latex_str1.replace("operatorname","mathrm")
latex_str2 = latex_str2.replace("operatorname","mathrm")
latex_str3 = latex_str3.replace("operatorname","mathrm")
plt.text(0.5, 0.5, latex_str1, fontsize=10, horizontalalignment='center')
plt.text(0.5, 0.3, latex_str2, fontsize=10, horizontalalignment='center')
plt.text(0.5, 0.1, latex_str3, fontsize=10, horizontalalignment='center')
plt.axis('off')
plt.show()

# the equations appear to be incredibly long, but simplification shows that they're the same as in
# A. Petzold - Realisierung eines Versuchsstandes zur Regelung des Balance-Brett-Systems
# chapter 2.2, page 11, equations (2.18),(2.19),(2.20)