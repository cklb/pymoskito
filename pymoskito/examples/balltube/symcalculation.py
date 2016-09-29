#!/usr/bin/python
# -*- coding: utf-8 -*-
import sympy as sp
import numpy as np
import pymoskito.tools as to

params = sp.symbols('x1, x2, x3, x4,'
                    'x1_d, x2_d, x3_d, x4_d, z,'
                    'xd_d0, xd_d1, xd_d2, xd_d3, xd_d4,'
                    'x1_e, x2_e, x3_e, x4_e, z_e,'
                    'u, l1, l2, l3, l1_star, l2_star, l3_star,'
                    'T, d, k_s, k_L, k_V, A_B, A_Sp, m, g,'
                    'x1_d_dot, x2_d_dot, x3_d_dot, x4_d_dot, x1_dot, c0, c1, c2')
x1, x2, x3, x4,\
x1_d, x2_d, x3_d, x4_d, z,\
xd_d0, xd_d1, xd_d2, xd_d3, xd_d4,\
x1_e, x2_e, x3_e, x4_e, z_e,\
u, l1, l2, l3, l1_star, l2_star, l3_star,\
T, d, k_s, k_L, k_V, A_B, A_Sp, m, g,\
x1_d_dot, x2_d_dot, x3_d_dot, x4_d_dot, x1_dot, c0, c1, c2 = params

x = sp.Matrix([x1, x2, x3, x4])
f_x = sp.Matrix([x2, -x1/T**2 - 2*d*x2/T, x4, (k_L*((k_V*x1 - A_B*x4)/A_Sp)**2 - m*g)/m])
g_x = sp.Matrix([0, k_s/T**2, 0, 0])
h_x = sp.Matrix([x3])

# calculate lie derivation
Lfh = to.lie_derivative(h_x, f_x, x, 1)
Lf2h = to.lie_derivative(h_x, f_x, x, 2)
Lf3h = to.lie_derivative(h_x, f_x, x, 3)
Lf4h = to.lie_derivative(h_x, f_x, x, 4)

LgLfh = to.lie_derivative(Lfh, g_x, x, 1)
LgLf2h = to.lie_derivative(Lf2h, g_x, x, 1)
LgLf3h = to.lie_derivative(Lf3h, g_x, x, 1)

y_d0 = h_x
y_d1 = Lfh
y_d2 = Lf2h + LgLfh
y_d3 = Lf3h + LgLf2h
y_d4 = Lf4h + LgLf2h


parameter = x1, x2, x3, x4, T, d, k_s, k_L, k_V, A_B, A_Sp, m, g
mat2array = [{'ImmutableMatrix': np.array}, 'numpy']
# y_d0_func = sp.lambdify(parameter, y_d0[0], modules=mat2array)  # trivial x3
# y_d1_func = sp.lambdify(parameter, y_d1[0], modules=mat2array)  # trivial x4
y_d2_func = sp.lambdify(parameter, y_d2[0], modules=mat2array)
y_d3_func = sp.lambdify(parameter, y_d3[0], modules=mat2array)

LgLf3h_func = sp.lambdify(parameter, LgLf3h[0], modules=mat2array)
Lf4h_func = sp.lambdify(parameter, Lf4h[0], modules=mat2array)
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
L_fan = sp.Matrix([[c1 - 2*d/T], [c0 - 2*d*(c1 - 2*d/T)/T - 1/T**2]])
L_fan_func = sp.lambdify((c0, c1, T, d), L_fan, modules=mat2array)

f_fan_e = sp.Matrix([[x2_e], [-x1_e/T**2 - 2*d*x2_e/T + k_s*u/T**2]])
f_fan_e_func = sp.lambdify((x1_e, x2_e, T, d, k_s, u), f_fan_e, modules=mat2array)

# observer for the second subsystem (ball)
C = sp.Matrix([[1, 0, 0]])
C_dot = sp.Matrix([[0, 0, 0]])
C_ddot = sp.Matrix([[0, 0, 0]])
L = sp.Matrix([l1, l2, l3])
L_star = sp.Matrix([l1_star, l2_star, l3_star])
x = sp.Matrix([x3, x4, z])
x_e = sp.Matrix([x3_e, x4_e, z_e])
x_dot = sp.Matrix([x4, (k_L*((k_V*x1 - A_B*x4)/A_Sp)**2 - m*g + z)/m, 0])
x_dot_e = sp.Matrix([x4_e, (k_L*((k_V*x1 - A_B*x4_e)/A_Sp)**2 - m*g + z_e)/m, 0])
x_dot_obs_error = x_dot - x_dot_e
A = x_dot_obs_error.jacobian(x)
A = A.subs([(x4, x4_d), (x1, x1_d)])
A_dot = A.subs([(x4_d, x4_d_dot), (x1_d, x1_d_dot)])
Q_B = sp.Matrix([C, C_dot + C*A, C_ddot + C_dot*A + C*A_dot + C_dot*A + C*A**2])
Q_B_inv = sp.inv_quick(Q_B)
e_3 = sp.Matrix([0, 0, 1])
t_1 = Q_B_inv*e_3
T = sp.Matrix([t_1.transpose(), (A*t_1).transpose(), (A**2*t_1).transpose()]).transpose()
T_inv = sp.inv_quick(T)
T_dot = sp.Matrix([[0, 0, 0], [0, 0, T[1,2]], [0, 0, 0]])
T_dot = T_dot.subs([(x4_d, x4_d_dot), (x1_d, x1_d_dot)])
A_star = T_inv*(A*T - T_dot)
A_star = A_star.expand()
C_star = C*T
lhs = A_star - L_star*C_star
A_d_star = sp.Matrix([[0, 0, -c0], [1, 0, -c1], [0, 1, -c2]])
equations = [sp.Eq(lhs[0, 2], A_d_star[0, 2]),
             sp.Eq(lhs[1, 2], A_d_star[1, 2]),
             sp.Eq(lhs[2, 2], A_d_star[2, 2])]
solution = sp.solve(equations, L_star)
L_star = sp.Matrix([solution[l1_star], solution[l2_star], solution[l3_star]])
L_ball = T*L_star
L_ball_func = sp.lambdify((c0, c1, c2, x1_d, x1_d_dot, x4_d, x4_d_dot, k_L, k_V, A_B, A_Sp, m, g), L_ball, modules=mat2array)

f_ball_e = sp.Matrix([[x4_e], [(k_L*((k_V*x1 - A_B*x4_e)/A_Sp)**2 - m*g + z_e)/m], [0]])
f_ball_e_func = sp.lambdify((x4_e, x1, z_e, k_L, k_V, A_B, A_Sp, m, g), f_ball_e, modules=mat2array)

x1_flat = (sp.sqrt((xd_d2 + g)*m*A_Sp**2/k_L) + A_B*xd_d1)/k_V
x2_flat = xd_d3*m*A_Sp**2/(2*k_V*k_L*(k_V*x1_flat - A_B*xd_d1)) + A_B*xd_d2/k_V

x1_flat_func = sp.lambdify((xd_d1, xd_d2, k_L, k_V, A_B, A_Sp, m, g), x1_flat, modules=mat2array)
x2_flat_func = sp.lambdify((xd_d1, xd_d2, xd_d3, k_L, k_V, A_B, A_Sp, m, g), x2_flat, modules=mat2array)
