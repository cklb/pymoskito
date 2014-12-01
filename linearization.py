# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 21:52:06 2014

Linearization in x_0

@author: Topher
"""

import sympy as sp
from sympy import sin,cos, Matrix

t = sp.Symbol('t')
params = sp.symbols('x, x1, x2, x3, x4, x01, x02, x03, x04, u1, tau, tau0, M , G , J , J_ball , R, B')
x, x1, x2, x3, x4, x01, x02, x03, x04, u1, tau, tau0, M , G , J , J_ball , R, B = params

#f1 = ddr
f1 = B*(x1*x4**2 - G*sin(x3))
#f2 = ddtheta
f2 = (tau - 2*M*x1*x2*x4 - M*G*x1*cos(x3))/(M*x1**2 + J + J_ball)

f1 = Matrix([f1])
f2 = Matrix([f2])

x = Matrix([[x1], [x2], [x3], [x4]])
# u1 ist der Eingang des ersten Systems wird zur Formellen Berechnung benötig
u = Matrix([[u1, tau]])

jac_A1 = f1.jacobian(x)
jac_A2 = f2.jacobian(x)
jac_B1 = f1.jacobian(u)
jac_B2 = f2.jacobian(u)

subs_list = [(x1,x01),(x2,x02),(x3,x03),(x4,x04),(tau,tau0)]
jac_A1 = jac_A1.subs(subs_list)
jac_A2 = jac_A2.subs(subs_list)
jac_B1 = jac_B1.subs(subs_list)
jac_B2 = jac_B2.subs(subs_list)

# Systemmatrix A
A = Matrix([[0, 1, 0, 0],\
            [jac_f1[0], jac_f1[1], jac_f1[2], jac_f1[3]],\
            [0, 0, 0, 1],\
            [jac_f2[0], jac_f2[1], jac_f2[2], jac_f2[3]]])

# Eingangsmatrix B
B = Matrix([[jac_B1[0]],\
            [jac_B1[1]],\
            [jac_B2[0]],\
            [jac_B2[1]]])
# Ausgangsmatrix
C = Matrix([[1, 0, 0, 0]])

# Steuerbarkeitsmatrix
Qs = Matrix([[C],[C*A],[C*A*A],[C*A*A*A]])
#muss ich noch umwandeln
