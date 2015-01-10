# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 21:52:06 2014

Linearization in x_0

@author: Topher
"""

import sympy as sp
import numpy as np

import settings as st

class Linearization:

    def __init__(self, x0, tau0):
        params = sp.symbols('x, x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B')
        x, x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B = params

        x01 = x0[0]
        x02 = x0[1]
        x03 = x0[2]
        x04 = x0[3]
        
        #f1 = ddr
        f1 = B*(x1*x4**2 - G*sp.sin(x3))
        #f2 = ddtheta
        f2 = (tau - 2*M*x1*x2*x4 - M*G*x1*sp.cos(x3))/(M*x1**2 + J + J_ball)
        
        f1 = sp.Matrix([f1])
        f2 = sp.Matrix([f2])
        
        x = sp.Matrix([[x1], [x2], [x3], [x4]])
        # u1 ist der Eingang des ersten Systems wird zur Formellen Berechnung benötig
        u = sp.Matrix([[u1, tau]])
        
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
        A = sp.Matrix([[0, 1, 0, 0],\
                    [jac_A1[0], jac_A1[1], jac_A1[2], jac_A1[3]],\
                    [0, 0, 0, 1],\
                    [jac_A2[0], jac_A2[1], jac_A2[2], jac_A2[3]]])
        
        # Eingangsmatrix B
        B = sp.Matrix([[jac_B1[0]],\
                    [jac_B1[1]],\
                    [jac_B2[0]],\
                    [jac_B2[1]]])
        # Ausgangsmatrix
        C = sp.Matrix([[1, 0, 0, 0]])

        #and we are done with sympy
        
        self.A = np.array(A).astype(float)
        self.B = np.array(B).astype(float)
        self.C = np.array(C).astype(float)

        # Steuerbarkeitsmatrix
        # Qs = Matrix([C, C*A, C*A**2, C*A**3])
        
    def calcPrefilter(self, K = None):
        '''
        calculate the prefilter and return a float
        '''
        # Vorfilter V = -[C(A-BK)^-1*B]^-1
        if K is not None:
            try:
                V = -np.linalg.inv(np.dot(np.dot(self.C,(np.linalg.inv(self.A-self.B*K))),self.B))[0][0]
            except np.linalg.linalg.LinAlgError:
                print 'Can not calculate V, because of a Singular Matrix'
                V = 1
        else:
            return 0
            
        return V   
    
    def ackerSISO(self, A, B, poles):
        '''        
        place poles and return a numpy row-matrix
           - place poles for a state feedback: you have to not transpose A and B
           - place poles for a observer: you have to transpose A and C,
             you will get a transposed L  
            
        '''
        
        #check consistency
        # TODO: throw an Exception clemens. no questionmarks.
        
        assert A.shape[0] == A.shape[1], 'A is not square'
        assert A.shape[0] == B.shape[0], 'dim(A) and dim (B) does not match'
        assert B.shape[1] == 1, 'dim(B) is not for SISO case'
        assert len(poles) == A.shape[0], 'dim(A) and dim(poles) does not match '
        
        n = A.shape[0]
        
        #n = len(poles)

        #starting smypy crap
        s = sp.symbols('s')
        
        poly = 1    
        for s_i in poles:
            poly = (s-s_i)*poly
        poly = poly.expand()
        
        p = []
        
        # calculate the coefficients of characteristic polynomion
        for i in range(n):
            p.append(poly.subs([(s,0)]))
            poly = poly - p[i]
            poly = poly/s
            poly = poly.expand()
        
        #ending sympy crap
        p = np.array(p).astype(float)
        
        # calculate controllability matrix
        QT = np.zeros((n, n))
        for i in range(n):
            QT[i, :] = (np.dot(np.linalg.matrix_power(A, i), B)).transpose()[0]
 
        Q = QT.transpose()

        # check rank and throw exception
        if (np.linalg.matrix_rank(Q) != n):
            raise Exception('System might not be controllable or observable')
            
        e_4 = np.zeros((1,n))
        e_4[0, n-1] = 1
        
        t1T = np.dot(e_4, np.linalg.inv(Q))
        
        cm = np.linalg.matrix_power(A, n)
        for i in range(n):
            cm = cm + p[i] * np.linalg.matrix_power(A, i)
        
        K = np.dot(t1T, cm)
        return K
        
