# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 21:52:06 2014

Linearization in x_0

@author: Topher
"""

import sympy as sp
import numpy as np
from sympy import sin,cos, Matrix
import settings as st


class Linearization:
    def __init__(self, x0 = None, tau0 = None):
        params = sp.symbols('x, x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B')
        x, x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B = params

        x01 = x0[0]
        x02 = x0[1]
        x03 = x0[2]
        x04 = x0[3]
        tau0 = tau0
        
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
        
        subs_list = [(x1,x01),(x2,x02),(x3,x03),(x4,x04),(tau,tau0),\
                    (B,st.B),(J,st.J),(J_ball, st.Jb),(M,st.M),(G,st.G),(R,st.R)]
        jac_A1 = jac_A1.subs(subs_list)
        jac_A2 = jac_A2.subs(subs_list)
        jac_B1 = jac_B1.subs(subs_list)
        jac_B2 = jac_B2.subs(subs_list)
        
        # Systemmatrix A
        self.A = Matrix([[0, 1, 0, 0],\
                    [jac_A1[0], jac_A1[1], jac_A1[2], jac_A1[3]],\
                    [0, 0, 0, 1],\
                    [jac_A2[0], jac_A2[1], jac_A2[2], jac_A2[3]]])
        
        # Eingangsmatrix B
        self.B = Matrix([[jac_B1[0]],\
                    [jac_B1[1]],\
                    [jac_B2[0]],\
                    [jac_B2[1]]])
        # Ausgangsmatrix
        self.C = Matrix([[1, 0, 0, 0]])
        
        # Steuerbarkeitsmatrix
        # Qs = Matrix([C, C*A, C*A**2, C*A**3])
    
    def calcFeedbackGain(self, poles):
        
        A = self.A
        B = self.B
        C = self.C
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
                
        t1T = Matrix([t1T1, t1T2, t1T3, t1T4])
        
        e_4 = Matrix([[0,0,0,1]])
        
        t1T = e_4*Qs**-1
        
        K = t1T*(A**4 + p[3]*A**(3) + p[2]*A**2 + p[1]*A + p[0]*sp.eye(4))
                        
        return self.symMatrixToNumArray(K)[0]
        
    def prefilter(self, K = None):
        A = self.symMatrixToNumArray(self.A)
        B = self.symMatrixToNumArray(self.B)
        C = self.symMatrixToNumArray(self.C)
        # Vorfilter V = -[C(A-BK)^-1*B]^-1
        if K is not None:
            V = -np.linalg.inv(np.dot(np.dot(C,(np.linalg.inv(A-B*K))),B))
        else:
            return 0

        return V[0]
        
    def symMatrixToNumArray(self, symMatrix = None):
        symMatrixShape = symMatrix.shape        
        numArray = np.zeros(symMatrixShape)
        for i in range(0,symMatrixShape[0]):
            for j in range(0,symMatrixShape[1]):
                numArray[i,j] = symMatrix[i,j]
        return numArray

