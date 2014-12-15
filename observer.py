# -*- coding: utf-8 -*-
import numpy as np
import sympy as sp
from sympy import sin,cos
from scipy.integrate import ode
import settings as st

from sim_core import SimulationModule
from linearization import Linearization

#---------------------------------------------------------------------
# obeserver base class 
#---------------------------------------------------------------------
class Observer(SimulationModule):

    def __init__(self):
        SimulationModule.__init__(self)
        return

    def getOutputDimension(self):
        return self.output_dim

    def observe(self, t, u, r):
        y = self.calcOutput(t, u, r)
        return y

#---------------------------------------------------------------------
# Luenberger Observer
#---------------------------------------------------------------------
class LuenbergerObserver(Observer):
    '''
    Luenberger Observer uses EULER integration
    '''

    settings = {\
            'initial state': [0, 0, 0, 0],\
            'poles': [-20, -20, -20, -20],\
            'lin state': [0, 0, 0, 0],\
            'lin tau': 0,\
            'tick divider': 1,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True
        
    def setStepWidth(self, width):
        self.step_width = width
              
    def stateFuncApprox(self, t, q):
        x_o = q
        y = np.array(self.sensor_output)
        u = self.controller_output

        dx_o = np.dot(self.A - np.dot(self.L, self.C), x_o) + self.B*u + self.L * y[0]
        
        return dx_o
        #return [dx1_o, dx2_o, dx3_o, dx4_o]
        
    def calcOutput(self, t, controller_output, sensor_output):
        if self.firstRun:
            self.lin = Linearization(self.settings['lin state'], self.settings['lin tau'])

            self.A = self.lin.A
            self.B = self.lin.B
            self.C = self.lin.C
            L_T = self.lin.ackerSISO(self.lin.A.transpose(),self.lin.C.transpose(),self.settings['poles'])
            self.L = L_T.transpose()
        
            self.x0 = self.settings['initial state']    #TODO set to zero    
            self.nextObserver_output = np.array([self.x0]).reshape(4,1)
            self.firstRun = False

        
        self.observer_output = self.nextObserver_output
        self.sensor_output = sensor_output
        self.controller_output = controller_output
        
        # sim_core Timer ist bereits einen Zeitschritt weiter
        dt = self.settings['tick divider']*self.step_width       
        dy = self.stateFuncApprox(t, self.observer_output)

        self.nextObserver_output = self.observer_output + dt*dy       
        return [float(self.observer_output[i, 0]) for i in range(self.observer_output.shape[0])]
        
#---------------------------------------------------------------------
# Luenberger Observer Reduced
#---------------------------------------------------------------------
class HighGainObserver(Observer):
    '''
    High Gain Observer for nonlinear systems
    '''

    settings = {\
           'initial state': [0, 0, 0, 0],\
            'poles': [-3, -3, -3, -3],\
            'tick divider': 1,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True

    def setStepWidth(self, width):
        self.step_width = width
        
    def lieDerivative(self, h, f, x, n):
        'calculates the Lie-Derivative from a skalarfield along a vectorfield'
        if n == 0:
            return h
        elif n == 1:
            return h.jacobian(x) * f
        else:
            return self.lieDerivative(self.lieDerivative(h, f, x, 1), f, x, n-1)
            
    def getCoefficients(self, poles):       
        s = sp.symbols('s')
        poly = 1    
        for s_i in poles:
            poly = (s-s_i)*poly
        poly = poly.expand()
        
        n = len(poles)
        p = []
        # calculate the coefficient of characteric polynom
        for i in range(n):
            p.append(poly.subs([(s,0)]))
            poly = poly - p[i]
            poly = poly/s
            poly = poly.expand()
            
        return p
    
    def symMatrixToNumArray(self, symMatrix = None):
        symMatrixShape = symMatrix.shape        
        numArray = np.zeros(symMatrixShape)
        for i in range(0,symMatrixShape[0]):
            for j in range(0,symMatrixShape[1]):
                numArray[i,j] = symMatrix[i,j]
        return numArray
    
        
    def calcOutput(self, t, controller_output, sensor_output):
        params = sp.symbols('x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B')
        x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B = params
        if self.firstRun:
            
            
            x = [x1, x2, x3, x4]
            self.h = sp.Matrix([[x1]])
            self.f = sp.Matrix([[x2],\
                                [B*x1*x4**2 - B*G*sin(x3)],\
                                [x4],\
                                [(tau - 2*M*x1*x2*x4 - M*G*x1*cos(x3))/(M*x1**2 + J + J_ball)]])
             
            q = sp.zeros(len(x), 1)
            for i in range(len(x)):
                q[i, 0] = self.lieDerivative(self.h, self.f, x, i)
            
#            print 'q', q
                
            dq = q.jacobian(x)
#            print 'dq', dq
            
            if (dq.rank() != len(x)):
                raise Exception('System might not be observable')
             
            # gets p = [p0, p1, ... pn-1]
            p = self.getCoefficients(self.settings['poles'])
#            print 'p', p
            
            k = sp.zeros(len(p), 1)           
            for i in range(1, len(p) + 1):
                k[i - 1, 0] = p[-i]
#            print 'k', k    
            
            #ATTENTION: I am in sympy so * should work
            self.l = dq.inv() * k
            
            self.x0 = self.settings['initial state']    
            self.nextObserver_output = np.array([self.x0]).reshape(4,1)
            self.firstRun = False

#        print '-'*30
        self.observer_output = self.nextObserver_output
        
        # ObserverOdeSolver reduced to EULER --> better performance
        # the output is calculated in a reduced transformated system
        
        dt = self.settings['tick divider']*self.step_width  
#        print
#        print 'controller_coutput', controller_output
#        print 'type(controller_outoput', type(controller_output)               
        u = controller_output
#        print 'u', u
#        print 'type(u)', type(u)
        # FIXME: sensor_output is here a (1,4) list but should only be the 
        # measured value and check sensor_output order after transformation
        # here: y is r, the distance
#        print
#        print 'sensor_output', sensor_output
#        print 'type(sensor_output', type(sensor_output)
        y = sp.Matrix([sensor_output[0]])
        
        dy = self.f + self.l*(y - self.h)
        
        #TODO: sub_list is not genearl
        subs_list = [(x1, self.observer_output[0,0]),\
                     (x2, self.observer_output[1,0]),\
                     (x3, self.observer_output[2,0]),\
                     (x4, self.observer_output[3,0]),\
                     (tau, u),\
                     (B,st.B),(J,st.J),(J_ball, st.Jb),(M,st.M),(G,st.G),(R,st.R)]
#        print
        dy = dy.subs(subs_list)
        dy = self.symMatrixToNumArray(dy)
        # EULER integration
        self.nextObserver_output = self.observer_output + dt * dy

        # we have the convention to return a list with shape (1, 4)
        return [float(self.observer_output[i, 0]) for i in range(self.observer_output.shape[0])]
        
        
#---------------------------------------------------------------------
# Luenberger Observer Reduced
#---------------------------------------------------------------------
class LuenbergerObserverReduced(Observer):
    '''
    Luenberger Observer Reduced
    '''

    settings = {\
           'initial state': [0, 0, 0, 0],\
            'poles': [-3, -3, -3],\
            'lin state': [0, 0, 0, 0],\
            'lin tau': 0,\
            'tick divider': 1,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True

    def setStepWidth(self, width):
        self.step_width = width
    
    def swap_cols(self, arr, frm, to):
        arr[:,[frm, to]] = arr[:,[to, frm]]
        return arr
        
    def swap_rows(self, arr, frm, to):
        arr[[frm, to],:] = arr[[to, frm],:]
        return arr
        
    def calcOutput(self, t, controller_output, sensor_output):
        if self.firstRun:
            self.lin = Linearization(self.settings['lin state'], self.settings['lin tau'])

            self.A = self.lin.A
            self.B = self.lin.B
            self.C = self.lin.C
            
            n = self.A.shape[0]
            r = self.C.shape[0]
            
            if self.C.shape != (1, 4):
                raise Exception('LuenbergerObserverReduced only useable for SISO')
                
            # which cols and rows must be sorted
            self.switch = 0
            for i in range(self.C.shape[1]):
                if self.C[0, i] == 1:
                    self.switch = i
                    break
                
            # sort A,B,C for measured and unmeasured states                
            self.A = self.swap_cols(self.A, 0, self.switch)
            self.A = self.swap_rows(self.A, 0, self.switch)
            
            self.C = self.swap_cols(self.C, 0, self.switch)
            
            self.B = self.swap_rows(self.B, 0, self.switch)

            # get reduced system
            self.A_11 = self.A[0:r, 0:r]  
            self.A_12 = self.A[0:r, r:n]
            self.A_21 = self.A[r:n, 0:r]
            self.A_22 = self.A[r:n, r:n]
            
            self.B_1 = self.B[0:r, :]
            self.B_2 = self.B[r:n, :]
            
            L_T = self.lin.ackerSISO(self.A_22.transpose(), self.A_12.transpose(), self.settings['poles'])
            self.L = L_T.transpose()
            
            # init observer
            self.x0 = self.settings['initial state']  
            self.nextObserver_output = np.array([self.x0]).reshape(4,1)
            self.firstRun = False

        
        self.observer_output = self.nextObserver_output
        
        # ObserverOdeSolver reduced to EULER --> better performance
        # the output is calculated in a reduced transformated system
        
        dt = self.settings['tick divider']*self.step_width      
        
        n = self.A.shape[0]
        r = self.C.shape[0]
        
        # transform ((un-)measured) and collect necessary from observer_output
        x_o = self.observer_output
        x_o = self.swap_rows(x_o, 0, self.switch)
        x_o = x_o[r:n, :]
           
        u = controller_output
        # FIXME: sensor_output is here a (1,4) list but should only be the 
        # measured value and check sensor_output order after transformation
        y = np.array(sensor_output) 
        # here: y is r, the distance
        y = y[0]
        
        # transform system, so you dont need ydot
        x_oTransf = x_o - self.L * y
        dy = np.dot(self.A_22 - np.dot(self.L, self.A_12), x_oTransf)\
            + (self.A_21 - np.dot(self.L, self.A_11) + np.dot(self.A_22 - np.dot(self.L, self.A_12), self.L)) * y\
            + (self.B_2 - np.dot(self.L, self.B_1)) * u
            
        # EULER integration
        x_oTransf_next = x_oTransf + dt * dy
        # transform system back to original observer coordinates
        x_o_next = x_oTransf_next + self.L * y
        
        observerOut = np.concatenate((np.array([[y]]), x_o_next), axis=0)   

        # change state order back to the original order
        self.nextObserver_output = self.swap_rows(observerOut, 0, self.switch)
        # we have the convention to return a list with shape (1, 4)
        return [float(self.observer_output[i, 0]) for i in range(self.observer_output.shape[0])]

#---------------------------------------------------------------------
# Luenberger Observer
#---------------------------------------------------------------------
class LuenbergerObserverInt(Observer):
    '''
    Luenberger Observer uses solver to integrate
    '''

    settings = {'Method': 'adams',\
            'step size': 0.01,\
            'rTol': 1e-6,\
            'aTol': 1e-9,\
            'end time': 10,\
            'initial state': [0, 0, 0, 0],\
            'poles': [-3, -3, -3, -3],\
            'lin state': [0, 0, 0, 0],\
            'lin tau': 0,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True
        
    def setStepWidth(self, width):
        self.step_width = width
              
    def stateFuncApprox(self, t, q):
        x1_o, x2_o, x3_o, x4_o = q
        y = np.array(self.sensor_output)
        u = self.controller_output

        x_o = np.array([[x1_o],\
                      [x2_o],\
                      [x3_o],\
                      [x4_o]])
        #FIXME: sensorausgang mit C vermanschen
        # ACHTUNG!!!! y[0] überdenken für mehrgrößenfall
        #y = np.dot(self.C, y.transpose())
        dx_o = np.dot(self.A - np.dot(self.L, self.C), x_o) + np.dot(self.B, u) + np.dot(self.L, y[0])
        
        dx1_o = dx_o[0, 0]
        dx2_o = dx_o[1, 0]
        dx3_o = dx_o[2, 0]
        dx4_o = dx_o[3, 0]
        
        
        return [dx1_o, dx2_o, dx3_o, dx4_o]
        
    def calcOutput(self, t, controller_output, sensor_output):
        if self.firstRun:
            self.lin = Linearization(self.settings['lin state'], self.settings['lin tau'])

            self.A = self.lin.A
            self.B = self.lin.B
            self.C = self.lin.C
            L_T = self.lin.ackerSISO(self.lin.A.transpose(),self.lin.C.transpose(),self.settings['poles'])
            self.L = L_T.transpose()
            
            self.solver = ode(self.stateFuncApprox)
            self.solver.set_integrator('dopri5', method=self.settings['Method'], \
                    rtol=self.settings['rTol'],\
                    atol=self.settings['aTol'])
            self.solver.set_initial_value(self.settings['initial state'])
        
            self.x0 = self.settings['initial state']    #TODO set to zero    
            self.nextObserver_output = self.x0
            self.firstRun = False

        
        self.observer_output = self.nextObserver_output
        self.sensor_output = sensor_output
        self.controller_output = controller_output
        
        # sim_core Timer ist bereits einen Zeitschritt weiter
        self.nextObserver_output = self.solver.integrate(t)           
        
        return self.observer_output
