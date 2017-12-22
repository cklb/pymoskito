# -*- coding: utf-8 -*-
import pickle
import numpy as np
import symbtools as symb

import pymoskito as pm
from model import global_public_settings, bb_shortcuts_for_readability, bb_sort_vector


class BBLinearController(pm.Controller):

    """"
    Linear Controller for the Balance Board system
    calculates its gain from symbolic model file
    linearizes system in chosen steady_theta
    """

    public_settings = global_public_settings.copy()
    # remove unnecessary entries again
    del public_settings["initial state"]
    del public_settings["constant of damping ground <-> board"]
    # add controller specific entries
    public_settings.update(poles=[-5, -5, -5, -5, -5, -5])
    public_settings.update(steady_theta=0)
    public_settings.update(partial=True)
    # reorder entries, important ones at the top
    public_settings.move_to_end('poles', last=False)
    public_settings.move_to_end('steady_theta', last=False)

    def __init__(self, settings):

        settings["steady_theta"] = np.deg2rad(settings["steady_theta"])
        settings.update(input_order=0)
        settings.update(input_type="system_state")
        pm.Controller.__init__(self, settings)

        # load precomputed state-space model
        with open("bal_board.pkl", "rb") as f:
            mod, params = pickle.load(f)

        if settings["partial"]:
            f_x = mod.ff
            g_x = mod.gg
        else:
            f_x = mod.f
            g_x = mod.g

        # resort state vector and functions, since JuPyter calculates with ttheta = [x1, x3, x2]
        x_vec = bb_sort_vector(self, mod.xx)
        f_x = bb_sort_vector(self, f_x)  #
        g_x = bb_sort_vector(self, g_x)  #

        # calculate system matrix
        a_matrix = f_x.jacobian(x_vec)  # this takes forever

        # load model parameters
        m1, xS1, yS1, I1, m2, yS2, I2, m3, yS3, I3, r, cB, cZ, g = bb_shortcuts_for_readability(self)
        z_ = [m1, xS1, yS1, I1, m2, 0, yS2, I2, m3, 0, yS3, I3, r, 0, 0, g, cB, cZ]
        subs_list = [(params[idx], z_[idx]) for idx in range(len(params))]

        # substitute placeholder with selected parameters
        self.steady_state, self.steady_input = calc_closest_steady_state(self, settings["steady_theta"])
        for idx in range(len(x_vec)):
            subs_list.append((x_vec[idx], self.steady_state[idx]))
        a_mat = a_matrix.subs(subs_list)        # this takes a while
        b_mat = g_x.subs(subs_list)

        a_func = symb.expr_to_func(x_vec, a_mat, np_wrapper=True)
        b_func = symb.expr_to_func(x_vec, b_mat, np_wrapper=True, eltw_vectorize=False)

        a_ = bb_make_array_6x6matrix(self, a_func(*x_vec))
        b_ = b_func(*x_vec)
        c_ = np.array([[0, 0, 1, 0, 0, 0]])

        # pole placement of linearized state feedback
        self._K = pm.controltools.place_siso(a_, b_, self._settings["poles"])
        self._V = pm.controltools.calc_prefilter(a_, b_, c_, self._K)[0][0]  # function returns array, store scalar only

    def _control(self, time, trajectory_values=None, feedforward_values=None,
                 input_values=None, **kwargs):
        x = input_values
        x0 = self.steady_state
        x_tilde = x - x0
        y_tilde = 0

        if trajectory_values is not None:
            yd = np.deg2rad(trajectory_values[0])
            y_tilde = yd - x0[2]

        u_tilde = -self._K @ x_tilde + self._V * y_tilde
        return u_tilde + self.steady_input


class BBGainSchedulingController(pm.Controller):

        """"
        Linear Controller, calculates its gain from symbolic model file
        stabilizes system close to initial position
        """

        public_settings = global_public_settings.copy()
        # remove unnecessary entries again
        del public_settings["initial state"]
        del public_settings["constant of damping ground <-> board"]
        # add controller specific entries
        public_settings.update(poles=[-5, -5, -5, -5, -5, -5])
        public_settings.update(partial=True)
        # reorder entries, important ones at the top
        public_settings.move_to_end('poles', last=False)

        def __init__(self, settings):

            settings.update(input_order=0)
            settings.update(input_type="system_state")
            pm.Controller.__init__(self, settings)

            # load precomputed state-space model
            with open("bal_board.pkl", "rb") as f:
                mod, params = pickle.load(f)

            if settings["partial"]:
                f_x = mod.ff
                g_x = mod.gg
            else:
                f_x = mod.f
                g_x = mod.g

            # resort state vector and functions, since JuPyter calculates with ttheta = [x1, x3, x2]
            self.x_vec = bb_sort_vector(self, mod.xx)
            f_x = bb_sort_vector(self, f_x)  #
            g_x = bb_sort_vector(self, g_x)  #

            # calculate system matrix
            a_matrix = f_x.jacobian(self.x_vec)  # this takes forever

            # load model parameters
            m1, xS1, yS1, I1, m2, yS2, I2, m3, yS3, I3, r, cB, cZ, g = bb_shortcuts_for_readability(self)
            z_ = [m1, xS1, yS1, I1, m2, 0, yS2, I2, m3, 0, yS3, I3, r, 0, 0, g, cB, cZ]
            subs_list = [(params[idx], z_[idx]) for idx in range(len(params))]

            self.a_mat = a_matrix.subs(subs_list)  # this takes a while
            self.b_mat = g_x.subs(subs_list)

        def _control(self, time, trajectory_values=None, feedforward_values=None,
                     input_values=None, **kwargs):

            x = input_values
            x0, steady_input = calc_closest_steady_state(self, x[2])
            x_tilde = x - x0

            y_tilde = 0
            if trajectory_values is not None:
                yd = np.deg2rad(trajectory_values[0])
                # overwrite previously calculated steady state
                #x0, steady_input = calc_closest_steady_state(self, yd)
                #y_tilde = x[2]-yd
                y_tilde = yd - x0[2]

            subs_list = [(self.x_vec[idx], x0[idx]) for idx in range(len(self.x_vec))]

            a_mat_x0 = self.a_mat.subs(subs_list)
            b_mat_x0 = self.b_mat.subs(subs_list)

            a_func = symb.expr_to_func(self.x_vec, a_mat_x0, np_wrapper=True)
            b_func = symb.expr_to_func(self.x_vec, b_mat_x0, np_wrapper=True, eltw_vectorize=False)

            a_ = bb_make_array_6x6matrix(self, a_func(*self.x_vec))
            b_ = b_func(*self.x_vec)
            c_ = np.array([[0, 0, 1, 0, 0, 0]])

            # pole placement of linearized state feedback
            k_ = pm.controltools.place_siso(a_, b_, self._settings["poles"])
            v_ = pm.controltools.calc_prefilter(a_, b_, c_, k_)

            u_tilde = -k_ @ x_tilde + v_ * y_tilde
            return u_tilde[0] + steady_input


def calc_closest_steady_state(self, theta):
    
    # definitional
    x3 = theta   # theta, cylinder angle

    m1, xS1, yS1, I1, m2, yS2, I2, m3, yS3, I3, r, cB, cZ, g = bb_shortcuts_for_readability(self)

    Psi_eq = -np.arcsin((m3*yS3)/(r*(m1+m2))*np.sin(x3))
    gamma_eq = (m1/m2*yS1 + yS2)*np.tan(Psi_eq) - r*(m1/m2 + 1)*(Psi_eq - x3) - m1/m2*xS1
    
    x_eq = np.array([Psi_eq, gamma_eq, x3, 0, 0, 0])
    F_eq = m2*g*np.sin(Psi_eq)
    
    return x_eq, F_eq


def bb_make_array_6x6matrix(self, array):
    matrix = np.vstack((array[0:6],
                        array[6:12],
                        array[12:18],
                        array[18:24],
                        array[24:30],
                        array[30:36]
                        ))
    return matrix
