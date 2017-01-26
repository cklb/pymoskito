# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp


# rcParams['text.usetex'] = True
# rcParams['text.latex.unicode'] = True


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

mat2array = [{'ImmutableMatrix': np.array}, 'numpy']  # settings for lambdify function

params = sp.symbols('x0_d0, x0_d1,'
                    ' phi1_d0, phi1_d1,'
                    ' phi2_d0, phi2_d1,'
                    ' m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2')

x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1,\
m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2 = params

term0 = m0 + m1*sp.sin(phi1_d0)**2 + m2*(sp.sin(phi2_d0))**2
term1 = m1*sp.sin(phi1_d0)*(g*sp.cos(phi1_d0) - l1*phi1_d1**2)
term2 = m2*sp.sin(phi2_d0)*(g*sp.cos(phi2_d0) - l2*phi2_d1**2)

x0_d2 = (term1 +
         term2 +
         (F - d0*x0_d1) +
         (M1 - d1*phi1_d1)*sp.cos(phi1_d0)/l1 +
         (M2 - d2*phi2_d1)*sp.cos(phi2_d0)/l2)/term0

phi1_d2 = g*sp.sin(phi1_d0)/l1 \
          + sp.cos(phi1_d0)*(term1 +
                             term2 +
                             (F - d0*x0_d1) +
                             (M1 - d1*phi1_d1)*sp.cos(phi1_d0)/l1 +
                             (M2 - d2*phi2_d1)*sp.cos(phi2_d0)/l2)/(l1*term0) \
          + (M1 - d1*phi1_d1)/(m1*l1**2)

phi2_d2 = g*sp.sin(phi2_d0)/l2 \
          + sp.cos(phi2_d0)*\
            (term1
             + term2
             + (F - d0*x0_d1)
             + (M1 - d1*phi1_d1)*sp.cos(phi1_d0)/l1
             + (M2 - d2*phi2_d1)*sp.cos(phi2_d0)/l2)\
            /(l2*term0) \
          + (M2 - d2*phi2_d1)/(m2*l2**2)

x = sp.Matrix([x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1])
# x = sp.Matrix([x0_d0, phi1_d0, phi2_d0, x0_d1, phi1_d1, phi2_d1])  # only for comparison
u = sp.Matrix([F, M1, M2])

sys = sp.Matrix([x0_d1, x0_d2, phi1_d1, phi1_d2, phi2_d1, phi2_d2])
# sys = sp.Matrix([x0_d1, phi1_d1, phi2_d1, x0_d2, phi1_d2, phi2_d2])  # only for comparison

dict_names = {x0_d0: r'x_{0}',
              x0_d1: r'\dot{x}_{0}',
              phi1_d0: r'\varphi_{1}',
              phi1_d1: r'\dot{\varphi}_{1}',
              phi2_d0: r'\varphi_{2}',
              phi2_d1: r'\dot{\varphi}_{2}'}
simplification_list = [(phi1_d1, 0), (phi2_d1, 0),
                       (F, 0), (M1, 0), (M2, 0),
                       # (sp.sin(phi1_d0), 0), (sp.sin(phi2_d0), 0),
                       # (sp.cos(phi1_d0)**2, 1), (sp.cos(phi2_d0)**2, 1),
                       # (sp.cos(phi1_d0)**3, sp.cos(phi1_d0)),
                       # (sp.cos(phi2_d0)**3, sp.cos(phi2_d0))
                       ]

A = sys.jacobian(x)
A = A.subs(simplification_list)
# preview(A, mode='equation', mat_str="array", symbol_names=dict_names)

# B with all control action (F, M1, M2)
B = sys.jacobian(u)
B = B.subs(simplification_list)
# preview(B, mode='equation', mat_str="array", symbol_names=dict_names)

# B with only F as control action
B = B[:, 0]

C = np.array([[1, 0, 0, 0, 0, 0]])

eq_state = [x0_d0, x0_d1, phi1_d0, phi1_d1,phi2_d0, phi2_d1]
parameter = [m0, m1, m2, l1, l2, g, d0, d1, d2]
A_func = sp.lambdify((eq_state, parameter), A, modules=mat2array)
B_func = sp.lambdify((eq_state, parameter), B, modules=mat2array)

# _eq_state = [0, 0, np.pi, 0, np.pi, 0]
# _parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
#
# A_num = A_func(_eq_state, _parameter)
# B_num = B_func(_eq_state, _parameter)
#
# K = to.ackerSISO(A_num, B_num, poles=[-10.1,-8.2,-6.9,-5,-2.5,-1.5])


params = sp.symbols('x0_d0, x0_d1,'
                    ' phi1_d0, phi1_d1,'
                    ' phi2_d0, phi2_d1,'
                    'u,'
                    ' m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2')

x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1, u,\
m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2 = params

x0_d2 = u

phi1_d2 = (g*sp.sin(phi1_d0))/l1 - (d1*phi1_d1)/(m1*l1**2) + (sp.cos(phi1_d0)*u)/l1

phi2_d2 = (g*sp.sin(phi2_d0))/l2 - (d2*phi2_d1)/(m2*l2**2) + (sp.cos(phi2_d0)*u)/l2

x_vec = sp.Matrix([x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1])
# x = sp.Matrix([x0_d0, phi1_d0, phi2_d0, x0_d1, phi1_d1, phi2_d1])  # only for comparison
u_vec = sp.Matrix([u])

sys = sp.Matrix([x0_d1, x0_d2, phi1_d1, phi1_d2, phi2_d1, phi2_d2])
# sys = sp.Matrix([x0_d1, phi1_d1, phi2_d1, x0_d2, phi1_d2, phi2_d2])  # only for comparison

dict_names = {x0_d0: r'x_{0}',
              x0_d1: r'\dot{x}_{0}',
              phi1_d0: r'\varphi_{1}',
              phi1_d1: r'\dot{\varphi}_{1}',
              phi2_d0: r'\varphi_{2}',
              phi2_d1: r'\dot{\varphi}_{2}'}
simplification_list = [(phi1_d1, 0), (phi2_d1, 0),
                       (F, 0), (M1, 0), (M2, 0), (u, 0)]

A_par_lin = sys.jacobian(x_vec)
A_par_lin = A_par_lin.subs(simplification_list)
# preview(A, mode='equation', mat_str="array", symbol_names=dict_names)

B_par_lin = sys.jacobian(u_vec)
B_par_lin = B_par_lin.subs(simplification_list)
# preview(B, mode='equation', mat_str="array", symbol_names=dict_names)

C_par_lin = np.array([[1, 0, 0, 0, 0, 0]])

eq_state = [x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1]
parameter = [m0, m1, m2, l1, l2, g, d0, d1, d2]
A_func_par_lin = sp.lambdify((eq_state, parameter), A_par_lin, modules=mat2array)
B_func_par_lin = sp.lambdify((eq_state, parameter), B_par_lin, modules=mat2array)

# _eq_state = [0, 0, np.pi, 0, np.pi, 0]
# _parameter = [st.m0, st.m1, st.m2, st.l1, st.l2, st.g, st.d0, st.d1, st.d2]
#
# A_num = A_func(_eq_state, _parameter)
# B_num = B_func(_eq_state, _parameter)
#
# K = to.ackerSISO(A_num, B_num, poles=[-10.1,-8.2,-6.9,-5,-2.5,-1.5])


