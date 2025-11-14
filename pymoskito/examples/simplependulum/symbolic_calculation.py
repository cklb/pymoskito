# -*- coding: utf-8 -*-

import numpy as np
import sympy as sp
from sympy import sin, cos
import matplotlib as mpl
import matplotlib.pyplot as plt

import pymoskito.tools as to


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

# Parameter
m0, m1, a1, l1, J1, d1, g, t = sp.symbols("m0, m1, a1, l1, J1, d1, g, t")

acc = sp.symbols("acc")  # Beschleunigung des Wagens
s, ds = sp.symbols("s, ds")
phi, dphi = sp.symbols("phi1, dphi1")

dict_names = {s: r's',
              ds: r'\dot{s}',
              phi: r'\varphi',
              dphi: r'\dot{\varphi}',
              }

ff = sp.Matrix([[ds], [dphi], [0], [1.0*(a1*g*m1*sin(phi) - d1*dphi)/(J1 + a1**2*m1)]])
gg = sp.Matrix([[0], [0], [1], [1.0*a1*m1*cos(phi)/(J1 + a1**2*m1)]])
xx = sp.Matrix([[s], [phi], [ds], [dphi]])
uu = sp.Matrix([acc])

A = ff.jacobian(xx)
# preview(A, mode='equation', mat_str="array", symbol_names=dict_names)

# B with all control action (F, M1, M2)
B = gg
# preview(B, mode='equation', mat_str="array", symbol_names=dict_names)

C = np.array([[1, 0, 0, 0]])

eq_state = [s, phi, ds, dphi]
parameter = [m0, m1, a1, l1, J1, d1, g]
A_func = sp.lambdify((eq_state, parameter), A, modules=mat2array)
B_func = sp.lambdify((eq_state, parameter), B, modules=mat2array)
