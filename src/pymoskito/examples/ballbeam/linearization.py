# -*- coding: utf-8 -*-
"""
Linearisation of the Ball and Beam system
"""

import sympy as sp
import numpy as np

from . import settings as st


def linearise_system(x0: np.ndarray, tau0: float) -> tuple:
    r"""
    Linearise the system at the steady state :math:`(\boldsymbol{x}^e, \tau^e)`
    
    Args:
        x0: Steady state.
        tau0: Corresponding system input.

    Returns:
        Tuple of matrices: Linear state space representation of the system.
    """
    params = sp.symbols('x, x1, x2, x3, x4, u1, tau, M , G , J , J_ball , R, B')
    x, x1, x2, x3, x4, u1, tau, M, G, J, J_ball, R, b = params

    x01 = x0[0]
    x02 = x0[1]
    x03 = x0[2]
    x04 = x0[3]

    # f1 = ddr
    f1 = b * (x1 * x4 ** 2 - G * sp.sin(x3))

    # f2 = ddtheta
    f2 = (tau - 2 * M * x1 * x2 * x4 - M * G * x1 * sp.cos(x3)) / (M * x1 ** 2
                                                                   + J + J_ball)

    f1 = sp.Matrix([f1])
    f2 = sp.Matrix([f2])

    x = sp.Matrix([[x1], [x2], [x3], [x4]])
    u = sp.Matrix([[u1, tau]])

    jac_a1 = f1.jacobian(x)
    jac_a2 = f2.jacobian(x)
    jac_b1 = f1.jacobian(u)
    jac_b2 = f2.jacobian(u)

    subs_list = [(x1, x01), (x2, x02), (x3, x03), (x4, x04), (tau, tau0),
                 (b, st.B), (J, st.J), (J_ball, st.Jb), (M, st.M), (G, st.G),
                 (R, st.R)]
    jac_a1 = jac_a1.subs(subs_list)
    jac_a2 = jac_a2.subs(subs_list)
    jac_b1 = jac_b1.subs(subs_list)
    jac_b2 = jac_b2.subs(subs_list)

    # system matrix A
    a = sp.Matrix([[0, 1, 0, 0],
                   [jac_a1[0], jac_a1[1], jac_a1[2], jac_a1[3]],
                   [0, 0, 0, 1],
                   [jac_a2[0], jac_a2[1], jac_a2[2], jac_a2[3]]
                   ])

    # input matrix B
    b = sp.Matrix([[jac_b1[0]],
                   [jac_b1[1]],
                   [jac_b2[0]],
                   [jac_b2[1]]
                   ])
    # output matrix C
    c = sp.Matrix([[1, 0, 0, 0]])

    # and we are done with sympy
    a_mat = np.array(a).astype(float)
    b_mat = np.array(b).astype(float)
    c_mat = np.array(c).astype(float)

    return a_mat, b_mat, c_mat


