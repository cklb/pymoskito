# -*- coding: utf-8 -*-
import numpy as np
import sympy as sp
from sympy import sin,cos
from scipy.integrate import ode
import settings as st

import tools as tools
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
            'poles': [-10, -10, -10, -10],\
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
        params = sp.symbols('x1, x2, x3, x4, tau')
        x1, x2, x3, x4, tau = params
        if self.firstRun:
            standards = sp.symbols('M , G , J , J_ball , R, B')
            M , G , J , J_ball , R, B = standards
            
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
            l = dq.inv() * k
            subs_list = [(B,st.B),(J,st.J),(J_ball, st.Jb),(M,st.M),(G,st.G),(R,st.R)]
            self.l = l.subs(subs_list)
            self.f = self.f.subs(subs_list)
            self.h = self.h.subs(subs_list)
#            print 'l', self.l
            
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
                     (tau, u)]
#        print
        dy = dy.subs(subs_list)
#        print 'dy', dy
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
            print 'A', self.A
            self.A = self.swap_rows(self.A, 0, self.switch)
            print 'A', self.A
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

#---------------------------------------------------------------------
# Nonlinear HighGainObserver von Christoph
#---------------------------------------------------------------------
class HighGainObserverChristoph(Observer):
    '''
    High Gain Observer for nonlinear systems
    '''

    settings = {\
           'initial state': [0, 0, 0, 0],\
            'poles': [-10, -10, -10, -10],\
            'tick divider': 1,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True
        
        x1, x2, x3, x4, u = sp.symbols('x1, x2, x3, x4, u')
        x = [x1, x2, x3, x4]
        
        h = sp.Matrix([[x1]])
        f = sp.Matrix([ [x2],\
                        [st.B*x1*x4**2 - st.B*st.G*sp.sin(x3)],\
                        [x4],\
                        [(u - 2*st.M*x1*x2*x4 - st.M*st.G*x1*sp.cos(x3))/(st.M*x1**2 + st.J + st.Jb)]])
#                        #[u]])

        q = sp.zeros(len(x), 1)
#        print 'f',f
#        print 'q', q
#        print 'type(q)', type(q)
        for i in range(len(x)):
            q[i, 0] = tools.lieDerivative(h, f, x, i)
        
        print 'q', q
        print 'type(q)', type(q)
            
        Q = q.jacobian(x)
#        print 'Q', Q
#        print 'type(Q)', type(Q)
        
        # gets p = [p0, p1, ... pn-1] as row-vector
        p = tools.getCoefficients(self.settings['poles'])
        print 'p', p
        print 'type(p)', type(p[0,0])
        self.k = np.zeros((p.shape[1], 1))           
        for i in range(1, p.shape[1] + 1):
            self.k[i - 1, 0] = p[0, -i]
        
#        print 'k', self.k
#        print 'type(k)', type(self.k)
        
        inv_Q = Q.inv()
        # create a lambda function which convert the Q and f matrix with the arguments 
        # of x1,x2,x3,x4 into a numpy array
        mat2array = [{'ImmutableMatrix': np.array}, 'numpy']
        self.inv_Q_func = sp.lambdify((x1,x2,x3,x4,u), inv_Q, modules = mat2array)
        self.f_func = sp.lambdify((x1,x2,x3,x4,u), f, modules = mat2array)
        
        
        

    def setStepWidth(self, width):
        self.step_width = width
        
    def stateFunc(self, x_o):
        h_x_o = np.array([x_o[0,0]])
        # measurment of r
        y = np.array([[self.sensor_output[0]]])
        u = self.controller_output
     
        Q_inv_np = self.inv_Q_func(x_o[0,0], x_o[1,0], x_o[2,0], x_o[3,0], u)
        f_np = self.f_func(x_o[0,0], x_o[1,0], x_o[2,0], x_o[3,0], u)
        
         
        dx_o = f_np + np.dot(np.dot(Q_inv_np,self.k),(y - h_x_o))
        
#        print 'x_o',x_o
#        print 'y',y
#        print 'u',u
#        print 'Q_inv_np',Q_inv_np
#        print 'f_np',f_np
#        print 'dx_o',dx_o
#        
#        print 'np.dot(Q_inv_np,self.k',np.dot(Q_inv_np,self.k)
#        print 'y - h_x_o',(y - h_x_o)
#        print 'np.dot(np.dot(Q_inv_np,self.k),(y - h_x_o))',np.dot(np.dot(Q_inv_np,self.k),(y - h_x_o))
        
        return dx_o
    
        
    def calcOutput(self, t, controller_output, sensor_output):
        
        self.controller_output = controller_output
        self.sensor_output = sensor_output

        if self.firstRun:
            self.x0 = self.settings['initial state']    
            self.nextObserver_output = np.array([self.x0]).reshape(4,1)
            self.firstRun = False

        self.observer_output = self.nextObserver_output
        
        # ObserverOdeSolver reduced to EULER --> better performance
        # the output is calculated in a reduced transformated system
        
        dt = self.settings['tick divider']*self.step_width
        # EULER integration
#        self.nextObserver_output = self.observer_output + dt * dy
        
        self.nextObserver_output = self.observer_output + dt * self.stateFunc(self.observer_output)
        # we have the convention to return a list with shape (1, 4)
        return [float(self.observer_output[i, 0]) for i in range(self.observer_output.shape[0])]


class HighGainObserverRefactored(Observer):
    '''
    High Gain Observer for nonlinear systems
    '''

    settings = {\
           'initial state': [0, 0, 0, 0],\
            'poles': [-10, -10, -10, -10],\
            'tick divider': 1,\
            }

    def __init__(self):
        self.output_dim = 4 #observer complete state
        Observer.__init__(self)
        self.firstRun = True

    def setStepWidth(self, width):
        self.step_width = width
        
    def calcOutput(self, t, controller_output, sensor_output):
        
        if self.firstRun: 
            params = sp.symbols('x1, x2, x3, x4, tau')
            x1, x2, x3, x4, tau = params
            x = [x1, x2, x3, x4]
            h = sp.Matrix([[x1]])
            f = sp.Matrix([[x2],\
                           [st.B*x1*x4**2 - st.B*st.G*sin(x3)],\
                           [x4],\
                           [(tau - 2*st.M*x1*x2*x4 - st.M*st.G*x1*cos(x3))/(st.M*x1**2 + st.J + st.Jb)]])
             
            q = sp.zeros(len(x), 1)
            for i in range(len(x)):
                q[i, 0] = tools.lieDerivative(h, f, x, i)
                
            dq = q.jacobian(x)
            
            if (dq.rank() != len(x)):
                raise Exception('System might not be observable')
             
            # gets p = [p0, p1, ... pn-1]
            p = tools.getCoefficients(self.settings['poles'])
            print 'type(p)', type(p[0,0])
                
            k = np.zeros((p.shape[1], 1))           
            for i in range(1, p.shape[1] + 1):
                k[i - 1, 0] = p[0, -i]    
            
            #ATTENTION: I am in sympy so * should work
            l = dq.inv() * k
            
            mat2array = [{'ImmutableMatrix': np.array}, 'numpy']
            self.h_func = sp.lambdify((x1,x2,x3,x4,tau), h, modules = mat2array)
            self.l_func = sp.lambdify((x1,x2,x3,x4,tau), l, modules = mat2array)
            self.f_func = sp.lambdify((x1,x2,x3,x4,tau), f, modules = mat2array)
            
            self.x0 = self.settings['initial state']    
            self.nextObserver_output = np.array([self.x0]).reshape(4,1)
            self.firstRun = False

        self.observer_output = self.nextObserver_output
                
        dt = self.settings['tick divider']*self.step_width  
              
        # FIXME: sensor_output is here a (1,4) list but should only be the 
        # measured value and check sensor_output order after transformation
        # here: y is r, the distance
        y = np.array([[sensor_output[0]]])
        u = controller_output
        
        l_np = self.l_func(self.observer_output[0,0],\
                           self.observer_output[1,0],\
                           self.observer_output[2,0],\
                           self.observer_output[3,0],\
                           u)
        f_np = self.f_func(self.observer_output[0,0],\
                           self.observer_output[1,0],\
                           self.observer_output[2,0],\
                           self.observer_output[3,0],\
                           u)
        h_x_o = self.h_func(self.observer_output[0,0], 0, 0, 0, 0)
        dx_o = f_np + np.dot(l_np,(y - h_x_o))
        
        # EULER integration
        self.nextObserver_output = self.observer_output + dt * dx_o

        # we have the convention to return a list with shape (1, 4)
        return [float(self.observer_output[i, 0]) for i in range(self.observer_output.shape[0])]


