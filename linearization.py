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
        
        self.A = self.symMatrixToNumArray(A)
        self.B = self.symMatrixToNumArray(B)
        self.C = self.symMatrixToNumArray(C)
        
        # Steuerbarkeitsmatrix
        # Qs = Matrix([C, C*A, C*A**2, C*A**3])
    
    def calcFeedbackGain(self, poles):
        n = len(poles)
        s = sp.symbols('s')
        
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
        QsT = np.array([self.B.transpose()[0],\
                     (np.dot(self.A, self.B)).transpose()[0],\
                     (np.dot(np.linalg.matrix_power(self.A,2),self.B)).transpose()[0],\
                     (np.dot(np.linalg.matrix_power(self.A,3),self.B)).transpose()[0]])
        Qs = QsT.transpose()
        
        if np.absolute(np.linalg.det(Qs)) < 0.0001:
            print 'Warning: System might not be controllable'
            print 'det(Qs):'
            print Qs.det()
        
        e_4 = np.array([0,0,0,1])
        
        t1T = np.dot(e_4,np.linalg.inv(Qs))
        
        K = np.dot(t1T,(np.linalg.matrix_power(self.A,4) + \
                        p[3]*np.linalg.matrix_power(self.A,3) + \
                        p[2]*np.linalg.matrix_power(self.A,2) + \
                        p[1]*self.A + \
                        p[0]*np.eye(4)))
        return K
        
    def calcPrefilter(self, K = None):
        # Vorfilter V = -[C(A-BK)^-1*B]^-1
        if K is not None:
            V = -np.linalg.inv(np.dot(np.dot(self.C,(np.linalg.inv(self.A-self.B*K))),self.B))[0][0]
        else:
            return 0

        return V
    
    def calcObserver(self, poles=None):
        
#        A = self.A
#        B = self.B
#        C = self.C
        
        n = len(poles)
        
        # check the observability
        Qb = np.array([(self.C)[0],\
                     (np.dot(self.C, self.A))[0],\
                     (np.dot(self.C, np.linalg.matrix_power(self.A, 2)))[0],\
                     (np.dot(self.C, np.linalg.matrix_power(self.A, 3)))[0]])
                     
        print Qb
        if np.absolute(np.linalg.det(Qb)) < 0.0001:
            print 'Warning: System might be not observable'
            print 'det(Qb):'
            print Qb.det()
            
        # just for special case x1, x3 measured
        cDesire = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])

        # SISO System, works for every x0, tau0   
        if self.C.shape[0] is 1:
            print 'observer: SISO'
            
            #TODO: per GUI die Messgröße, dh C einstellen lassen
            
            s = sp.symbols('s')

            # CLCP desire
            poly = 1    
            for s_i in poles:
                poly = (s-s_i)*poly
            poly = poly.expand()
            
            # calculate the coefficient of characteric polynom
            p = []
            for i in range(n):
                p.append(poly.subs([(s,0)]))
                poly = poly - p[i]
                poly = poly/s
                poly = poly.expand()
            
            # last column of the inverted observer matrix
            en_4 = np.array([[0],[0],[0],[1]])
            v1 = np.dot(np.linalg.inv(Qb), en_4)
            
            # there where some 
            p0 = p[0]
            p1 = p[1]
            p2 = p[2]
            p3 = p[3]
            
            L = np.dot(p[0]*np.eye(n) + \
                        p[1]*self.A + \
                        p[2]*np.linalg.matrix_power(self.A, 2) + \
                        p[3]*np.linalg.matrix_power(self.A, 3) + \
                        np.linalg.matrix_power(self.A, 4), v1)
                        
        
        # useable for C =[1, 0 ,0 ,0;
        #                 0, 0, 1, 0]
        # and x0 = 0 and tau0 = 0
        #TODO: noch AP in if-Bedigung checken, muss dann aber anders übergeben
        # werden
        elif (self.C.shape[0] is 2) and (np.array_equal(self.C, cDesire)):
            
            print 'observer: SIMO'
            # place(A', C',poles) of Matlab did not work
            # so l21=l22=l32=l42 = 1 setted
            # poles are placed by [-3,-3,-3,-3]
            L = np.array([[11, 1],\
                          [34.9712, 1],\
                          [-7.0288, 1],\
                          [-30.2717, 1]])
            
        elif min(self.C.shape) > 1:
            print 'momentan nicht implementiert, vllt durch Carsten Skript'
            print 'brauche place MIMO'
            L = np.array([[0],[0],[0],[0]])
        
        return L    
    
    def symMatrixToNumArray(self, symMatrix = None):
        symMatrixShape = symMatrix.shape        
        numArray = np.zeros(symMatrixShape)
        for i in range(0,symMatrixShape[0]):
            for j in range(0,symMatrixShape[1]):
                numArray[i,j] = symMatrix[i,j]
        return numArray

# operating point
q_op = [0, 0, 0, 0]
tau_op = 0
poles_LSSController = [-2, -2, -2, -2]

l = Linearization(q_op,tau_op)
K = l.calcFeedbackGain(poles_LSSController)
print K
V = l.calcPrefilter(K)
print V

L = l.calcObserver([-3,-3,-3,-3])
print L