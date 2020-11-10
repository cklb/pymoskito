# -*- coding: utf-8 -*-
import pickle
import symbtools as symb
from collections import OrderedDict
import numpy as np

import pymoskito as pm

import settings as st


global_public_settings = OrderedDict([("initial state", st.init),
                                      #----------board----------
                                      ("board mass", st.m1),
                                      ("board centre of gravity x-direction", st.xS1),
                                      ("board centre of gravity y-direction", st.yS1),
                                      ("board inertia",st.I1),
                                      ("board length",st.L1),
                                      #----------carriage----------
                                      ("carriage mass", st.m2),
                                      ("carriage centre of gravity y-direction", st.yS2),
                                      ("carriage inertia",st.I2),
                                      #----------cylinder----------
                                      ("cylinder mass", st.m3),
                                      ("cylinder centre of gravity y-direction", st.yS3),
                                      ("cylinder inertia",st.I3),
                                      ("cylinder radius",st.r),
                                      #----------damping----------
                                      ("constant of damping board <-> cylinder",st.cB),
                                      ("constant of damping ground <-> cylinder",st.cZ),
                                      ("constant of damping ground <-> board",st.cG),
                                      #----------gravity----------
                                      ("gravity", st.g),])


class ReducedBalanceBoardModel(pm.Model):
    r'''
    Implementation of the balance board model.
    Equations taken from [Petzold], changes taken from [Räbiger]
    Model is reduced by fixing the cylinder in its initial position
    -> theta = theta dot = 0
    output is the board deflection Psi
    '''

    public_settings = global_public_settings.copy()

    def __init__(self, settings):

        # conversion from degree to radiant
        settings["initial state"] = bb_initial_deg2rad(self, settings)

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
        0: {"Name": "board deflection", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

    def state_function(self, t, x, args):

        # definitional
        x1 = x[0]   # psi, board deflection
        x2 = x[1]   # gamma, carriage position
        x3 = x[2]   # theta, cylinder angle
        x4 = x[3]   # psi dot , board rotational velocity
        x5 = x[4]   # gamma dot, carriage velocity
        x6 = x[5]   # theta dot, cylinder rotational velocity
        
        F  = args[0][0]# force on mass is input

        # load model parameters
        m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g = bb_shortcuts_for_readability(self)
        
        # terms to help out
        delta = x1 * r + xS1
        eps   = x1 * r + x2 #epsilon

        P11   = m1 *(delta**2 + yS1**2) + m2 *(eps**2 + yS2**2) + I1 + I2
        P12   = -m2*yS2
        P21   = -yS2
        P22   = 1

        B1    = -((m1 * r * delta + m2 * r * eps) * x4**2 + (2 * m2 * eps * x5 +cB) * x4 +
                 g * m1 * (delta * np.cos(x1) - yS1 * np.sin(x1)) + g * m2 * (eps * np.cos(x1) - yS2 * np.sin(x1)))
        B2    = F/m2 + eps * x4**2 - g * np.sin(x1)
        
        P_mat = np.array([[P11,P12],
                          [P21,P22]
                         ])
        P_inv = np.linalg.inv(P_mat)
        B_mat = np.array([B1,B2])
        
        dx_vec = np.dot(P_inv,B_mat)
        
        # model equations
        dx1 = x4
        dx2 = x5
        dx3 = x6
        dx4 = np.dot(dx_vec,np.array([1,0]))
        dx5 = np.dot(dx_vec,np.array([0,1]))
        dx6 = 0    # due to reduced model
        
        dx = np.array([dx1,dx2,dx3,dx4,dx5,dx6])
        return dx

    def check_consistency(self, x):
    
        bb_check_consistency(self, x)
        
    def root_function(self,x):
        
        return bb_root_function(self,x)
        
    def calc_output(self, input_vector):
        
        psi   = input_vector[0]
        return [psi]

class ReducedBalanceBoardModelParLin(pm.Model):


    public_settings = global_public_settings.copy()

    def __init__(self, settings):
        
        # conversion from degree to radiant
        settings["initial state"] = bb_initial_deg2rad(self, settings)

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
        0: {"Name": "board deflection", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

    def state_function(self, t, x, args):

        # definitional
        x1 = x[0]   # psi, board deflection
        x2 = x[1]   # gamma, carriage position
        x3 = x[2]   # theta, cylinder angle
        x4 = x[3]   # psi dot , board rotational velocity
        x5 = x[4]   # gamma dot, carriage velocity
        x6 = x[5]   # theta dot, cylinder rotational velocity
        
        u  = args[0]# acceleration of mass is input
        
        # load model parameters
        m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g = bb_shortcuts_for_readability(self)

        #  terms to help out
        roh = x1 * r + x2
        z = I1 + I2 + m1 * ((x1*r + xS1)**2 + yS1**2) + m2 * (roh**2 + yS2**2)

        f3 = ((-x4 * (cB + 2 * x5 * m2 * roh + x4 * r * (m1*(x1*r + xS1) + m2*roh))
                - g * (m1 * (x1 * r + xS1) + m2 * roh) * np.cos(x1) 
                + g * (m1 * yS1 + m2 * yS2) * np.sin(x1))
              / z)
        g3 = ((m2 * yS2) 
              / z)
        
        dx1 = x4
        dx2 = x5
        dx3 = x6
        dx4 = f3 + g3 * u
        dx5 = u
        dx6 = 0
        
        dx = np.array([dx1,dx2,dx3,dx4,dx5,dx6])
        return dx

    def check_consistency(self, x):
    
        bb_check_consistency(self, x)
        
    def root_function(self,x):
        
        return bb_root_function(self,x)
        
    def calc_output(self, input_vector):
        
        psi   = input_vector[0]
        return [psi]
        
        
class BalanceBoardModel(pm.Model):
    r'''
    Implementation of the balance board model.
    Equations taken from [Petzold], changes taken from [Räbiger]
    All components moveable.
    '''

    public_settings = global_public_settings.copy()
    
    def __init__(self, settings):
    
        # conversion from degree to radiant
        settings["initial state"] = bb_initial_deg2rad(self, settings)

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
        0: {"Name": "cylinder angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

    def state_function(self, t, x, args):

        # definitional
        x1 = x[0]   # psi, board deflection
        x2 = x[1]   # gamma, carriage position
        x3 = x[2]   # theta, cylinder angle
        x4 = x[3]   # psi dot , board rotational velocity
        x5 = x[4]   # gamma dot, carriage velocity
        x6 = x[5]   # theta dot, cylinder rotational velocity
        
        F  = args[0][0]# force on mass is input
        
        # load model parameters
        m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g = bb_shortcuts_for_readability(self)


        # terms to help out
        delta = r*(x1-x3) + xS1 
        eps   = r*(x1-x3) + x2 #epsilon
        cos_1 = np.cos(x1) + 1
        
        C1 = -cB*x4 - m1*r*delta*(x4 - 2*x6)*x4 - g*m1*(delta*np.cos(x1) - yS1*np.sin(x1)) - m2*eps*(r*(x4 - 2*x6) + 2*x5)*x4 - g*m2*(eps*np.cos(x1) - yS2*np.sin(x1))
        C2 = F/m2 + eps*x4**2 - g*np.sin(x1)
        C3 = -cZ*x6 - m1*r*(delta*cos_1 + (r - yS1)*np.sin(x1))*x4**2 + 2*(m1 + m2)*r**2*np.sin(x1)*x4*x6 + g*(m1 + m2)*r*np.sin(x1) - m2*r*(eps*cos_1 + (r-yS2)*np.sin(x1))*x4**2 - 2*m2*r*np.sin(x1)*x4*x5 + m3*r*yS3*np.sin(x3)*x6**2 + g*m3*yS3*np.sin(x3)
        
        C_mat = np.array([C1,C2,C3])
        
        Q11  = m1*(delta**2 + yS1**2) + m2*(eps**2 + yS2**2) + I1 + I2
        Q12  = -m2*yS2
        Q13  = m1*r*(delta*np.sin(x1) + yS1*cos_1) + m2*r*(eps*np.sin(x1) + yS2*cos_1)
        Q21  = -yS2
        Q22  = 1
        Q23  = -r*cos_1
        Q31  = m1*r*(delta*np.sin(x1) + yS1*cos_1) + m2*r*(eps*np.sin(x1) + yS2*cos_1)
        Q32  = -m2*r*cos_1
        Q33  = 2*(m1 + m2)*r**2*cos_1 + m3*(r**2 + 2*r*yS3*np.cos(x3) + yS3**2) + I3
        
        Q_mat = np.array([[Q11,Q12,Q13],
                          [Q21,Q22,Q23],
                          [Q31,Q32,Q33]
                         ])
        Q_inv = np.linalg.inv(Q_mat)
        
        dx_vec = np.dot(Q_inv,C_mat)
        
        # model equations
        dx1 = x4
        dx2 = x5
        dx3 = x6
        dx4 = np.dot(dx_vec,np.array([1,0,0]))
        dx5 = np.dot(dx_vec,np.array([0,1,0]))
        dx6 = np.dot(dx_vec,np.array([0,0,1]))
        
        dx = np.array([dx1,dx2,dx3,dx4,dx5,dx6])
        return dx

    def check_consistency(self, x):
    
        bb_check_consistency(self, x)
        
    def root_function(self,x):
        
        # bypass root function:
        #return [False,x]
        return bb_root_function(self,x)
        
    def calc_output(self, input_vector):

        theta = input_vector[2]
        return [theta]
        
        
class BalanceBoardModelParLin(pm.Model):
    r'''
    Implementation of the balance board model.
    Partially linearized.
    Equations taken from [Petzold], changes taken from [Räbiger]
    All components moveable.
    '''

    public_settings = global_public_settings.copy()

    def __init__(self, settings):
    
        # conversion from degree to radiant
        settings["initial state"] = bb_initial_deg2rad(self, settings)

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
        0: {"Name": "cylinder angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

    def state_function(self, t, x, args):

        # definitional
        x1 = x[0]   # psi, board deflection
        x2 = x[1]   # gamma, carriage position
        x3 = x[2]   # theta, cylinder angle
        x4 = x[3]   # psi dot , board rotational velocity
        x5 = x[4]   # gamma dot, carriage velocity
        x6 = x[5]   # theta dot, cylinder rotational velocity
        
        u  = args[0][0]# acceleration of mass is input
        
        # load model parameters
        m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g = bb_shortcuts_for_readability(self)


        # terms to help out
        delta = r*(x1-x3) + xS1 
        eps   = r*(x1-x3) + x2 #epsilon
        cos_1 = np.cos(x1) + 1
        
        C1 = -cB*x4 - m1*r*delta*(x4 - 2*x6)*x4 - g*m1*(delta*np.cos(x1) - yS1*np.sin(x1)) - m2*eps*(r*(x4 - 2*x6) + 2*x5)*x4 - g*m2*(eps*np.cos(x1) - yS2*np.sin(x1)) + m2*yS2*u
        C2 = u
        C3 = -cZ*x6 - m1*r*(delta*cos_1 + (r - yS1)*np.sin(x1))*x4**2 + 2*(m1 + m2)*r**2*np.sin(x1)*x4*x6 + g*(m1 + m2)*r*np.sin(x1) - m2*r*(eps*cos_1 + (r-yS2)*np.sin(x1))*x4**2 - 2*m2*r*np.sin(x1)*x4*x5 + m3*r*yS3*np.sin(x3)*x6**2 + g*m3*yS3*np.sin(x3) + m2*r*cos_1*u
        
        C_mat = np.array([C1,C2,C3])
        
        Q11  = m1*(delta**2 + yS1**2) + m2*(eps**2 + yS2**2) + I1 + I2
        Q12  = 0
        Q13  = m1*r*(delta*np.sin(x1) + yS1*cos_1) + m2*r*(eps*np.sin(x1) + yS2*cos_1)
        Q21  = 0
        Q22  = 1
        Q23  = 0
        Q31  = m1*r*(delta*np.sin(x1) + yS1*cos_1) + m2*r*(eps*np.sin(x1) + yS2*cos_1)
        Q32  = 0
        Q33  = 2*(m1 + m2)*r**2*cos_1 + m3*(r**2 + 2*r*yS3*np.cos(x3) + yS3**2) + I3
        
        Q_mat = np.array([[Q11,Q12,Q13],
                          [Q21,Q22,Q23],
                          [Q31,Q32,Q33]
                         ])
        Q_inv = np.linalg.inv(Q_mat)
        
        dx_vec = np.dot(Q_inv,C_mat)
        
        # model equations
        dx1 = x4
        dx2 = x5
        dx3 = x6
        dx4 = np.dot(dx_vec,np.array([1,0,0]))
        dx5 = np.dot(dx_vec,np.array([0,1,0]))
        dx6 = np.dot(dx_vec,np.array([0,0,1]))
        
        dx = np.array([dx1,dx2,dx3,dx4,dx5,dx6])
        return dx

    def check_consistency(self, x):
    
        bb_check_consistency(self, x)
        
    def root_function(self,x):
        
        return bb_root_function(self,x)
        
    def calc_output(self, input_vector):

        theta = input_vector[2]
        return [theta]


class SymbolicBalanceBoardModel(pm.Model):
    """
    Model that uses a symbolic expressions derived by  an CAS
    """

    public_settings = global_public_settings.copy()
    public_settings.update(partial=False)

    def __init__(self, settings):
        
        # conversion from degree to radiant
        settings["initial state"] = bb_initial_deg2rad(self, settings)

        # add specific "private" settings
        settings.update(state_count=6)
        settings.update(input_count=1)
        settings.update({"output_info": {
            0: {"Name": "cylinder angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # load model parameters
        m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g = bb_shortcuts_for_readability(self)
        d1 = 1  # board height
        d2 = 1  # carriage height

        # load precomputed state-space model
        with open("bal_board.pkl", "rb") as pkl:
            mod, params = pickle.load(pkl)

        # substitute placeholder with selected parameters
        z_ = [m1, xS1, yS1, I1, m2, 0, yS2, I2, m3, 0, yS3, I3, r, d1, d2, g, cB, cZ]
        subs_list = [(params[idx], z_[idx]) for idx in range(len(params))]

        if self._settings["partial"]:
            f_x = mod.ff.subs(subs_list)
            g_x = mod.gg.subs(subs_list)
        else:
            f_x = mod.f.subs(subs_list)
            g_x = mod.g.subs(subs_list)
        
        # resort state vector, since JuPyter calculates with ttheta = [x1, x3, x2]
        x_vec = bb_sort_vector(self, mod.xx)
        f_x = bb_sort_vector(self, f_x)
        g_x = bb_sort_vector(self, g_x)

        self.f_func = symb.expr_to_func(x_vec, f_x, np_wrapper=True)
        self.g_func = symb.expr_to_func(x_vec, g_x, np_wrapper=True, eltw_vectorize=False)


    def state_function(self, t, x, args):
        u = args[0]
        ret = self.f_func(*x) + self.g_func(*x) @ u
        return ret
        
    def check_consistency(self, x):
    
        bb_check_consistency(self, x)
        
    def root_function(self,x):
        
        return bb_root_function(self,x)
        
    def calc_output(self, input_vector):

        theta = input_vector[2]
        return [theta]


def bb_sort_vector(self, wrong_order):
    # resort state vector, since JuPyter calculates with ttheta = [x1, x3, x2]
    right_order = wrong_order.copy()
    right_order[2] = wrong_order[1]
    right_order[1] = wrong_order[2]
    right_order[5] = wrong_order[4]
    right_order[4] = wrong_order[5]
    
    return right_order


def bb_initial_deg2rad(self, settings):
    initial = settings["initial state"]
    
    # conversion from degree to radiant
    initial[0] = np.deg2rad(initial[0])
    initial[2] = np.deg2rad(initial[2])
    initial[3] = np.deg2rad(initial[3])
    initial[5] = np.deg2rad(initial[5])
    
    return initial


def bb_shortcuts_for_readability(self):
    m1  = self._settings["board mass"]
    xS1 = self._settings["board centre of gravity x-direction"]
    yS1 = self._settings["board centre of gravity y-direction"]
    I1  = self._settings["board inertia"]
    m2  = self._settings["carriage mass"]
    yS2 = self._settings["carriage centre of gravity y-direction"]
    I2  = self._settings["carriage inertia"]
    m3  = self._settings["cylinder mass"]
    yS3 = self._settings["cylinder centre of gravity y-direction"]
    I3  = self._settings["cylinder inertia"]
    r   = self._settings["cylinder radius"]
    cB  = self._settings["constant of damping board <-> cylinder"]
    cZ  = self._settings["constant of damping ground <-> cylinder"]
    g   = self._settings["gravity"]
    
    return m1,xS1,yS1,I1,m2,yS2,I2,m3,yS3,I3,r,cB,cZ,g


def bb_check_consistency(self, x):

    x1 = x[0]   # psi, board deflection
    x2 = x[1]   # gamma, carriage position
    x3 = x[2]   # theta, cylinder angle
    
    L1 = self._settings["board length"]
    r  = self._settings["cylinder radius"] 
    
    # mass leaves board
    if abs(x2) > (L1/2):
        raise pm.ModelException("The carriage left the board.")
    # board leaves cylinder by angle
    if abs(x1) > (np.pi/2):
        raise pm.ModelException("Board reached critical angle.")
    # board leaves cylinder by touching point B
    if np.abs(r*(x1-x3)) > (L1/2):
        raise pm.ModelException("The board fell off the cylinder")


def bb_root_function(self,x):

    x_new = x
    flag = False

    x1 = x[0]   # psi, board deflection
    x2 = x[1]   # gamma, carriage position
    x3 = x[2]   # theta, cylinder angle
    
    L1 = self._settings["board length"]
    r  = self._settings["cylinder radius"] 
    cG = self._settings["constant of damping ground <-> board"]

    # calculate v-component of current position of lower board corner
    s3        = np.array([-r*x3,0])
    R_Psi     = np.array([[np.cos(x1), -np.sin(x1)],
                          [np.sin(x1),  np.cos(x1)]])
    xy_corner = np.array([r*(x1-x3) - np.sign(x1)*L1/2, r])
    e_v       = np.array([0,1])
    v_corner  = np.dot(e_v, s3 + np.dot(R_Psi, xy_corner))
    
    # make the board bounce back up
    if v_corner < -r:
        x_new[3] = -x[3]*(1-cG)
        flag = True
    
    return [flag, x_new]