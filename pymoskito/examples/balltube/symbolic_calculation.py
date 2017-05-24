# -*- coding: utf-8 -*-

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

import pymoskito as pm
import settings as st

from matplotlib import rcParams
rcParams['text.usetex'] = True


def preview(expr, **kwargs):
    """
    support function to display nice formula
    :param expr:
    :param kwargs:
    :return:
    """
    latex_str = sp.latex(expr, **kwargs)
    latex_str = latex_str.replace("operator_name", "mathrm")
    plt.text(0.1, 0.1, latex_str, fontsize=20)
    plt.axis('off')
    plt.show()

mat2array = [{'ImmutableMatrix': np.array}, 'numpy']
params = sp.symbols('x1, x2, x3, x4,'
                    'x1_d, x2_d, x3_d, x4_d, z,'
                    'xd_d0, xd_d1, xd_d2, xd_d3, xd_d4,'
                    'x1_e, x2_e, x3_e, x4_e, z_e,'
                    'u, l1, l2, l3, l1_star, l2_star, l3_star,'
                    'T, d, k_s, k_L, k_V, A_B, A_Sp, m, g,'
                    'x1_d_dot, x2_d_dot, x3_d_dot, x4_d_dot, x1_dot, c0, c1, c2')
x1, x2, x3, x4, \
    x1_d, x2_d, x3_d, x4_d, z, \
    xd_d0, xd_d1, xd_d2, xd_d3, xd_d4, \
    x1_e, x2_e, x3_e, x4_e, z_e, \
    u, l1, l2, l3, l1_star, l2_star, l3_star, \
    T, d, k_s, k_L, k_V, A_B, A_Sp, m, g, \
    x1_d_dot, x2_d_dot, x3_d_dot, x4_d_dot, x1_dot, c0, c1, c2 = params

dict_names = {x1_d: r'x_{1}^{d}',
              x2_d: r'x_{2}^{d}',
              x3_d: r'x_{3}^{d}',
              x4_d: r'x_{4}^{d}',
              }

x = sp.Matrix([x1, x2, x3, x4])
x_e = sp.Matrix([x1_e, x2_e, x3_e, x4_e])
f_x = sp.Matrix([x2, -x1 / T ** 2 - 2 * d * x2 / T,
                 x4,
                 (k_L * ((k_V * x1 - A_B * x4) / A_Sp) ** 2 - m * g) / m])
g_x = sp.Matrix([0, k_s / T ** 2, 0, 0])
h_x = sp.Matrix([x3])

# preview(f_x, mode='equation', mat_str="array", symbol_names=dict_names)
# preview(g_x, mode='equation', mat_str="array", symbol_names=dict_names)

# linearization
simplification_list = [(x1, A_Sp*sp.sqrt(m*g/k_L)/k_V),
                       (x2, 0),
                       (x3, x3_e),
                       (x4, 0),
                       (u, A_Sp*sp.sqrt(m*g/k_L)/(k_V*k_s))]
sys = f_x + g_x*u
A_lin = sys.jacobian(x)
A_lin = A_lin.subs(simplification_list)
B_lin = sys.jacobian(sp.Matrix([u]))
B_lin = B_lin.subs(simplification_list)
C_lin = h_x.jacobian(x)
C_lin = C_lin.subs(simplification_list)
D_lin = h_x.jacobian(sp.Matrix([u]))
D_lin = D_lin.subs(simplification_list)
# preview(A_lin, mode='equation', mat_str="array", symbol_names=dict_names)
# preview(B_lin, mode='equation', mat_str="array", symbol_names=dict_names)
# preview(C_lin, mode='equation', mat_str="array", symbol_names=dict_names)
# preview(D_lin, mode='equation', mat_str="array", symbol_names=dict_names)

x_e_list = [x3_e]
parameter_list = [T, d, k_s, k_L, k_V, A_B, A_Sp, m, g]
A_func = sp.lambdify((x_e_list + parameter_list), A_lin, modules=mat2array)
B_func = sp.lambdify((x_e_list + parameter_list), B_lin, modules=mat2array)
C_func = sp.lambdify((x_e_list + parameter_list), C_lin, modules=mat2array)
D_func = sp.lambdify((x_e_list + parameter_list), D_lin, modules=mat2array)

A_num = A_func(0, st.T, st.d, st.k_s, st.k_L, st.k_V, st.A_B, st.A_Sp, st.m, st.g)
B_num = B_func(0, st.T, st.d, st.k_s, st.k_L, st.k_V, st.A_B, st.A_Sp, st.m, st.g)
C_num = C_func(0, st.T, st.d, st.k_s, st.k_L, st.k_V, st.A_B, st.A_Sp, st.m, st.g)
D_num = D_func(0, st.T, st.d, st.k_s, st.k_L, st.k_V, st.A_B, st.A_Sp, st.m, st.g)

# check controlability for state feedback
Q_c = np.concatenate((B_num,
                      A_num @ B_num,
                      np.linalg.matrix_power(A_num, 2) @ B_num,
                      np.linalg.matrix_power(A_num, 3) @ B_num), axis=1)
n = np.rank(Q_c)  # system is not controllable, because n=2 < 4 system order

# check controlability for state feedback with I-controller
A_cross = np.concatenate((np.concatenate((A_num, C_num), axis=0),
                          np.zeros((A_num.shape[0] + C_num.shape[0],
                                    C_num.shape[0]))),
                         axis=1)
B_cross = np.concatenate((B_num, np.zeros((C_num.shape[0], B_num.shape[1]))),
                         axis=0)
C_cross = np.concatenate((C_num, np.zeros((C_num.shape[0], C_num.shape[0]))),
                         axis=1)
Q_c_cross = np.concatenate((B_num,
                            A_num @ B_num,
                            np.linalg.matrix_power(A_num, 2) @ B_num,
                            np.linalg.matrix_power(A_num, 3) @ B_num,
                            np.linalg.matrix_power(A_num, 4) @ B_num),
                           axis=1)

# system is not controllable, because n=2 < 5 system order
n = np.rank(Q_c_cross)


# calculate lie derivatives
Lfh_n = pm.lie_derivatives(h_x, f_x, x, 4)
LgLfh = pm.lie_derivatives(Lfh_n[1], g_x, x, 1)
LgLf2h = pm.lie_derivatives(Lfh_n[2], g_x, x, 1)
LgLf3h = pm.lie_derivatives(Lfh_n[3], g_x, x, 1)

y_d0 = h_x
y_d1 = Lfh_n[1]
y_d2 = Lfh_n[2] + LgLfh
y_d3 = Lfh_n[3] + LgLf2h
y_d4 = Lfh_n[4] + LgLf3h

parameter = x1, x2, x3, x4, T, d, k_s, k_L, k_V, A_B, A_Sp, m, g
# y_d0_func = sp.lambdify(parameter, y_d0[0], modules=mat2array)  # trivial x3
# y_d1_func = sp.lambdify(parameter, y_d1[0], modules=mat2array)  # trivial x4
y_d2_func = sp.lambdify(parameter, y_d2[0], modules=mat2array)
y_d3_func = sp.lambdify(parameter, y_d3[0], modules=mat2array)

LgLf3h_func = sp.lambdify(parameter, LgLf3h[0], modules=mat2array)
Lf4h_func = sp.lambdify(parameter, Lfh_n[4][0], modules=mat2array)
f_func = sp.lambdify(parameter, f_x, modules=mat2array)
g_func = sp.lambdify(parameter, g_x, modules=mat2array)
h_func = sp.lambdify(parameter, h_x, modules=mat2array)

# some considerations about observability
# observability map
q = sp.Matrix([y_d0, y_d1, y_d2, y_d3])
# observability matrix
Q = q.jacobian(x)
Q_inv = sp.inv_quick(Q)
Q_inv_func = sp.lambdify(parameter, Q_inv, modules=mat2array)

# observer for the first subsystem (fan)
L_fan = sp.Matrix([[c1 - 2 * d / T],
                   [c0 - 2 * d * (c1 - 2 * d / T) / T - 1 / T ** 2]])
L_fan_func = sp.lambdify((c0, c1, T, d), L_fan, modules=mat2array)

f_fan_e = sp.Matrix([[x2_e],
                     [-x1_e / T ** 2 - 2 * d * x2_e / T + k_s * u / T ** 2]])
f_fan_e_func = sp.lambdify((x1_e, x2_e, T, d, k_s, u),
                           f_fan_e,
                           modules=mat2array)

# observer for the second subsystem (ball)
C = sp.Matrix([[1, 0, 0]])
C_dot = sp.Matrix([[0, 0, 0]])
C_ddot = sp.Matrix([[0, 0, 0]])
L = sp.Matrix([l1, l2, l3])
L_star = sp.Matrix([l1_star, l2_star, l3_star])

x = sp.Matrix([x3, x4, z])
x_e = sp.Matrix([x3_e, x4_e, z_e])
x_dot = sp.Matrix([x4,
                   (k_L * ((k_V * x1 - A_B * x4) / A_Sp) ** 2 - m * g + z) / m,
                   0])
x_dot_e = sp.Matrix([x4_e,
                     (k_L * ((k_V * x1 - A_B * x4_e) / A_Sp) ** 2
                      - m * g + z_e) / m,
                     0])
x_dot_obs_error = x_dot - x_dot_e

A = x_dot_obs_error.jacobian(x)
A = A.subs([(x4, x4_d), (x1, x1_d)])
A_dot = A.subs([(x4_d, x4_d_dot), (x1_d, x1_d_dot)])
Q_B = sp.Matrix([C,
                 C_dot + C * A,
                 C_ddot + C_dot * A + C * A_dot + C_dot * A + C * A ** 2])
Q_B_inv = sp.inv_quick(Q_B)

e_3 = sp.Matrix([0, 0, 1])
t_1 = Q_B_inv * e_3
T = sp.Matrix([t_1.transpose(),
               (A * t_1).transpose(),
               (A ** 2 * t_1).transpose()]).transpose()
T_inv = sp.inv_quick(T)
T_dot = sp.Matrix([[0, 0, 0],
                   [0, 0, T[1, 2]],
                   [0, 0, 0]])
T_dot = T_dot.subs([(x4_d, x4_d_dot),
                    (x1_d, x1_d_dot)])
A_star = T_inv * (A * T - T_dot)
A_star = A_star.expand()
C_star = C * T
lhs = A_star - L_star * C_star
A_d_star = sp.Matrix([[0, 0, -c0], [1, 0, -c1], [0, 1, -c2]])
equations = [sp.Eq(lhs[0, 2], A_d_star[0, 2]),
             sp.Eq(lhs[1, 2], A_d_star[1, 2]),
             sp.Eq(lhs[2, 2], A_d_star[2, 2])]
solution = sp.solve(equations, L_star)
L_star = sp.Matrix([solution[l1_star], solution[l2_star], solution[l3_star]])
L_ball = T * L_star
L_ball_func = sp.lambdify((c0, c1, c2, x1_d, x1_d_dot, x4_d, x4_d_dot, k_L, k_V,
                           A_B, A_Sp, m, g),
                          L_ball,
                          modules=mat2array)

f_ball_e = sp.Matrix([[x4_e],
                      [(k_L * ((k_V * x1 - A_B * x4_e) / A_Sp) ** 2
                        - m * g + z_e) / m],
                      [0]])
f_ball_e_func = sp.lambdify((x4_e, x1, z_e, k_L, k_V, A_B, A_Sp, m, g),
                            f_ball_e,
                            modules=mat2array)

x1_flat = (sp.sqrt((xd_d2 + g) * m * A_Sp ** 2 / k_L) + A_B * xd_d1) / k_V
x2_flat = (xd_d3 * m * A_Sp ** 2 / (2 * k_V * k_L * (k_V * x1_flat
                                                     - A_B * xd_d1))
           + A_B * xd_d2 / k_V)

x1_flat_func = sp.lambdify((xd_d1, xd_d2, k_L, k_V, A_B, A_Sp, m, g),
                           x1_flat,
                           modules=mat2array)
x2_flat_func = sp.lambdify((xd_d1, xd_d2, xd_d3, k_L, k_V, A_B, A_Sp, m, g),
                           x2_flat,
                           modules=mat2array)
