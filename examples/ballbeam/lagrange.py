# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 20:28:06 2014

Lagrange formalism

@author: Topher
"""

import sympy as sp
from sympy import sin,cos,Function

t = sp.Symbol('t')
params = sp.symbols('M , G , J , J_ball , R')
M , G , J , J_ball , R = params

# ball position r
r_t = Function('r')(t)
d_r_t = r_t.diff(t)
dd_r_t = r_t.diff(t,2)
# beam angle theta
theta_t = Function('theta')(t)
d_theta_t = theta_t.diff(t)
dd_theta_t = theta_t.diff(t,2)
# torque of the beam
tau = Function('tau')

# kinetic energy
T = ((M + J_ball/R**2)*d_r_t**2 + (J + M*r_t**2 + J_ball)*d_theta_t**2)/2

# potential energy
V = M*G*r_t*sin(theta_t)

# lagrange function
L = T - V

# replace functions through symbols
r_s , d_r_s , dd_r_s , theta_s, d_theta_s , dd_theta_s = sp.symbols('r_s , d_r_s , dd_r_s , theta_s, d_theta_s , dd_theta_s')
subs_list = [(dd_r_t,dd_r_s),(dd_theta_t,dd_theta_s),(d_r_t,d_r_s),(d_theta_t,d_theta_s),(r_t,r_s),(theta_t,theta_s)]
L = L.subs(subs_list)

# simplify L
L = L.expand()
L = sp.trigsimp(L)

# assitant terms
d_L_r = L.diff(r_s)
d_L_theta = L.diff(theta_s)

d_L_d_r = L.diff(d_r_s)
d_L_d_theta = L.diff(d_theta_s)

# replace symbols through functions
subs_list_rev = []
for tup in subs_list:
    subs_list_rev.append((tup[1],tup[0]))

#d_L_r = d_L_r.subs(subs_list_rev)
#d_L_theta = d_L_theta.subs(subs_list_rev)

d_L_d_r = d_L_d_r.subs(subs_list_rev)
d_L_d_theta = d_L_d_theta.subs(subs_list_rev)

# derivate to time
dt_d_L_d_r = d_L_d_r.diff(t)
dt_d_L_d_theta = d_L_d_theta.diff(t)

# replace functions through symbols
dt_d_L_d_r = dt_d_L_d_r.subs(subs_list)
dt_d_L_d_theta = dt_d_L_d_theta.subs(subs_list)

# lagrange equation
Eq_r = dt_d_L_d_r - d_L_r
Eq_theta = dt_d_L_d_theta - d_L_theta

#Eq_r = Eq_r.factor()
#Eq_theta = Eq_theta.factor()

Eq_r = sp.Eq(0 , Eq_r)
Eq_theta = sp.Eq(tau , Eq_theta)

r_s , d_r_s , dd_r_s , theta_s, d_theta_s , dd_theta_s
# symbols in latex-notation
sn_dict = {r_s: r'r', d_r_s: r'\dot{r}', dd_r_s: r'\ddot{r}',
           theta_s: r' \theta', d_theta_s: r'\dot{\theta}', dd_theta_s: r'\ddot{\theta}'}


# show lagrange equation
import matplotlib.pyplot as plt
latex_str1 = "$ %s $" % sp.latex(Eq_r,symbol_names = sn_dict)
latex_str2 = "$ %s $" % sp.latex(Eq_theta,symbol_names = sn_dict)
latex_str1 = latex_str1.replace("operatorname","mathrm")
latex_str2 = latex_str2.replace("operatorname","mathrm")
plt.text(0.5, 0.5, latex_str1, fontsize=30, horizontalalignment='center')
plt.text(0.5, 0.3, latex_str2, fontsize=30, horizontalalignment='center')
plt.axis('off')
plt.show()