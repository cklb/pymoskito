#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

import settings as st
from tools import getCoefficients
from linearization import Linearization
from sim_core import SimulationModule

#---------------------------------------------------------------------
# controller base class 
#---------------------------------------------------------------------
class Controller(SimulationModule):

    order = 0

    def __init__(self):
        SimulationModule.__init__(self)

    def getOrder(self):
        return self.order

    def getOutputDimension(self):
        #no extra necessary all the same
        return 1

    def control(self, x, w):
        u = self.calcOutput(x, w)
        tau = u * (st.M*x[0]**2 + st.J + st.Jb)\
                + st.M* (2*x[0]*x[1]*x[3] + st.G*x[0]*np.cos(x[2]))
        return tau

    def setStepWidth(self, width):
        return

#---------------------------------------------------------------------
#P controller
#---------------------------------------------------------------------
#class PController(Controller):
    #'''
    #PController
    #- e.g. inital states x = [0, 0.2, 0, 0], desired position r = 0
    #'''
    
    #controller gain
    #Kp = -0.6
    
    #def __init__(self):
        #self.order = 0
        #Controller.__init__(self)
        
    #def calcOutput(self, x, w):
        #u = self.Kp*(w[0]-x[0])
        #return u

#---------------------------------------------------------------------
# controller created by changing f(x) 
#---------------------------------------------------------------------
class FController(Controller):

    settings = {\
                'poles': [-2, -2, -2, -2],\
                'tick divider': 1,\
                }
    # controller gains

    def __init__(self):
        self.order = 4
        self.firstRun = True
        Controller.__init__(self)

    def calcOutput(self, x, yd):
        if self.firstRun:
            self.k = getCoefficients(self.settings['poles'])[0]
            self.firstRun = False
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -st.B*st.G*np.sin(x[2])
        phi4 = -st.B*st.G*x[3]*np.cos(x[2])
        
        # calculate fictional input v
        v = yd[4] + \
                self.k[3]*(yd[3] - phi4) + \
                self.k[2]*(yd[2] - phi3) + \
                self.k[1]*(yd[1] - phi2) + \
                self.k[0]*(yd[0] - phi1)
        
        # calculate a(x)
        a = -st.B*st.G*np.cos(x[2])
        # calculate b(x)
        b = st.B*st.G*x[3]**2*np.sin(x[2])
        
        # calculate u
        u = (v-b)/a
        
        #print phi1, phi2, phi3, phi4
        #print a, b, v, u
        return u

#---------------------------------------------------------------------
# controller created by changing g(x) 
#---------------------------------------------------------------------
class GController(Controller):
    
    settings = {\
                'poles': [-2, -2, -2, -2],\
                'tick divider': 1,\
                }
    
    def __init__(self):
        self.order = 4
        self.firstRun = True
        Controller.__init__(self)
        
    def calcOutput(self, x, yd):
        if self.firstRun:
            self.k = getCoefficients(self.settings['poles'])[0]
            self.firstRun = False
            
        # calculate nonlinear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -st.B*st.G*np.sin(x[2]) + st.B*x[0]*x[3]**2
        phi4 = -st.B*st.G*x[3]*np.cos(x[2]) + st.B*x[1]*x[3]**2
        
        # calculate fictional input v
        v = yd[4] + \
                self.k[3]*(yd[3] - phi4) + \
                self.k[2]*(yd[2] - phi3) + \
                self.k[1]*(yd[1] - phi2) + \
                self.k[0]*(yd[0] - phi1)
        
        # calculate a(x)
        a = -st.B*st.G*np.cos(x[2]) + 2*st.B*x[1]*x[3]
        # calculate b(x)
        b = st.B**2+x[0]*x[3]**4 + st.B*st.G*(1 - st.B)*x[3]**2*np.sin(x[2])
        
        # calculate u
        u = (v-b)/a
        
        return u

#---------------------------------------------------------------------
# controller based on the standard jacobian approximation
#---------------------------------------------------------------------
class JController(Controller):
    
    settings = {\
                'poles': [-2, -2, -2, -2],\
                'tick divider': 1,\
                }

    def __init__(self):
        self.order = 4
        self.firstRun = True
        Controller.__init__(self)
    
    def calcOutput(self, x, yd):
        if self.firstRun:
            self.k = getCoefficients(self.settings['poles'])[0]
            self.firstRun = False
        
        # calculate linear terms phi
        phi1 = x[0]
        phi2 = x[1]  
        phi3 = -st.B*st.G*x[2]
        phi4 = -st.B*st.G*x[3]
        
        # calculate fictional input v
        v = yd[4] + \
                self.k[3]*(yd[3] - phi4) + \
                self.k[2]*(yd[2] - phi3) + \
                self.k[1]*(yd[1] - phi2) + \
                self.k[0]*(yd[0] - phi1)
        
        # calculate a(x)
        a = -st.B*st.G/(st.J + st.Jb)
        # calculate b(x)
        b = st.B*st.M*st.G**2*x[0]/(st.J + st.Jb)
        
        # calculate u
        u = (v-b)/a
        
        return u

#---------------------------------------------------------------------
# linear statespace controller
#---------------------------------------------------------------------
class LSSController(Controller):
    '''
    linear statespace controller
    System is linearised by tau0 and x = [x01,x02,x03,x04]
    '''

    settings = {\
            'poles': [-2, -2, -2, -2],\
            'r0': 0,\
            'tick divider': 1,\
            }

    def __init__(self):
        Controller.__init__(self)
        self.firstRun = True
        self.order = 0
        
    def calcOutput(self, x, yd):
        # x as row-matrix
        x = np.array([[x[0],x[1],x[2],x[3]]])
        if self.firstRun:
            self.lin = Linearization([self.settings['r0'], 0, 0, 0],\
                    self.settings['r0'] * st.M*st.G)         
            self.K = self.lin.ackerSISO(self.lin.A, self.lin.B, self.settings['poles'])
            self.V = self.lin.calcPrefilter(self.K)
            self.firstRun = False
            
        # calculate u
        u = np.dot(-self.K,np.transpose(x))[0,0] + yd[0]*self.V

        return u
        
#---------------------------------------------------------------------
# Input-Output-Linearization
#---------------------------------------------------------------------
class IOLController(Controller):
    '''
    Input-Output-Linearisation-Controller with managed non well defined 
    relative degree
    - this controller fails!!!
    '''
    # controller gains
    settings = {\
            'k' : [8.0, 12.0, 6.0],\
            'tick divider': 1,\
        }
    
    def __init__(self):
        self.order = 3
        Controller.__init__(self)
        
    def calcOutput(self, x, yd):

        # calculate y terms
        y = x[0]
        y_d = x[1]
        y_dd = st.B*x[0]*x[3]**2 -st.B*st.G*np.sin(x[2]) 
        
        # calculate fictional input v
        v = yd[3] + \
                self.settings['k'][2]*(yd[2] - y_dd) + \
                self.settings['k'][1]*(yd[1] - y_d) + \
                self.settings['k'][0]*(yd[0] - y)
        
        # calculate a(x)
        a = 2*st.B*x[0]*x[3]
        # calculate b(x)
        b = st.B*x[1]*x[3]**2 - st.B*st.G*x[3]*np.cos(x[2])
    
        # calculate u
        if np.absolute(a) < 0.3:     
            u = 0
        else:
            u = (v-b)/a

        return u

#---------------------------------------------------------------------
# PIFeedbackController
#---------------------------------------------------------------------
class PIFeedbackController(Controller):
    '''
    linear statespace controller
    System is linearised by tau0 and x = [x01,x02,x03,x04]
    with I-controller
    '''
    settings = {\
            'poles': [-2, -2, -2, -2, -2],\
            'r0': 0,\
            'tick divider': 1,\
            }

    def __init__(self):
        Controller.__init__(self)
        self.firstRun = True
        self.order = 0
        self.e_old = 0

    def setStepWidth(self, width):
        self.step_width = width

    def calcOutput(self, x, yd):
        
        # x as row-matrix
        x = np.array([[x[0],x[1],x[2],x[3]]])
        if self.firstRun:
            self.lin = Linearization([self.settings['r0'], 0, 0, 0],\
                    self.settings['r0'] * st.M*st.G)


            # build a A and B matrix with a new component of e for error of the position
            A_trans = np.concatenate((self.lin.A, self.lin.C), axis = 0)
            
            # now we have to add zeros with r rows and c columns
            r = A_trans.shape[0]
            c = A_trans.shape[0]-A_trans.shape[1]
            zero = np.zeros((r,c))
            A_trans = np.concatenate((A_trans, zero), axis=1)
            
            B_trans = self.lin.B
            # now we have to add zeros with r rows and c columns
            r = A_trans.shape[0] - self.lin.B.shape[0]
            c = B_trans.shape[1]
            zero = np.zeros((r,c))
            B_trans = np.concatenate((self.lin.B, zero), axis=0)
            K_trans = self.lin.ackerSISO(A_trans, B_trans, self.settings['poles'])
            # split K_trans in K and K_I          
            # select all element in row matrix of K_trans except the last one
            # and create numpy row matrix
            # the syntax is necessary for numpy's characteristics:
            # somehow, getting row number one reduces the dimension of the tensor 
            self.K = np.array([K_trans[0,0:-1]])
            # last element in row matrix of K_trans
            self.K_I = K_trans[0,-1]
            
            # calculate V
            self.V = self.lin.calcPrefilter(self.K)
            self.firstRun = False
        
        # calculate e
        e = (yd-x[0,0])*self.step_width + self.e_old
        self.e_old = e                        

        # calculate u
        u = np.dot(-self.K,np.transpose(x))[0,0] + self.K_I*e + self.V*yd[0]

        return u
