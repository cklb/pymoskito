# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 21:52:06 2014

Linearization in x_0

"""
import settings as st
import sympy as sp
from sympy import sin,cos, Matrix

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

subs_list = [(x1,3),(x2,0),(x3,0),(x4,0),(tau,st.M*st.G*3)]\
#,(B,st.B),(J,st.J),(J_ball, st.Jb),(M,st.M),(G,st.G),(R,st.R)]
#subs_list = [(x1,x01),(x2,x02),(x3,x03),(x4,x04),(tau,tau0)]
jac_A1 = jac_A1.subs(subs_list)
jac_A2 = jac_A2.subs(subs_list)
jac_B1 = jac_B1.subs(subs_list)
jac_B2 = jac_B2.subs(subs_list)

# Systemmatrix A
A = Matrix([[0, 1, 0, 0],\
            [jac_A1[0], jac_A1[1], jac_A1[2], jac_A1[3]],\
            [0, 0, 0, 1],\
            [jac_A2[0], jac_A2[1], jac_A2[2], jac_A2[3]]])

# Eingangsmatrix B
B = Matrix([[jac_B1[0]],\
            [jac_B1[1]],\
            [jac_B2[0]],\
            [jac_B2[1]]])
# Ausgangsmatrix
C = Matrix([[1, 0, 0, 0]])

# Beobachtbarkeitsmatrix
Qb = Matrix([C, C*A, C*A**2, C*A**3])
print 'Qb: ',Qb
QsT = Matrix([B.transpose(),\
             (A*B).transpose(),\
             (A**2*B).transpose(),\
             (A**3*B).transpose()])
Qs = QsT.transpose()
print 'Qs: ',Qs


def calcFeedbackGain(A, B, poles):
    n = len(poles)
    param = sp.symbols('s, t1T1, t1T2, t1T3, t1T4')
    s, t1T1, t1T2, t1T3, t1T4 = param
    
    poly = 1    
    for s_i in poles:
        poly = (s-s_i)*poly
    poly = poly.expand()
    
    p = []
    
    # calculate the coefficient of characteric polynom
    for i in range(n):
#        print i
#        print poly.subs([(s,0)])
        p.append(poly.subs([(s,0)]))
        poly = poly - p[i]
        poly = poly/s
        poly = poly.expand()
    
    
    # calculate controllability matrix
    QsT = Matrix([B.transpose(),\
                 (A*B).transpose(),\
                 (A**2*B).transpose(),\
                 (A**3*B).transpose()])
    Qs = QsT.transpose()
    print 'Qs: ',Qs
    det_Qs = Qs.det()
#    print det_Qs.expand()
    
    
    t1T = Matrix([t1T1, t1T2, t1T3, t1T4])
    
    e_4 = Matrix([[0,0,0,1]])
    
    t1T = e_4*Qs**-1
    
    K = t1T*(A**4 + p[3]*A**(3) + p[2]*A**2 + p[1]*A + p[0]*sp.eye(4))
    return K

#poles = [-2, -2, -2, -2]
#K = calcFeedbackGain(A, B, poles)
#print 'K: ',K
