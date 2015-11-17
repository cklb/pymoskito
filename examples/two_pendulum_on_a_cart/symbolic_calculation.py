import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['text.usetex'] = True
# rcParams['text.latex.unicode'] = True

def preview(expr, **kwargs):
    """
    support function to diyplay nice formula
    :param expr:
    :param kwargs:
    :return:
    """
    latex_str = sp.latex(expr, **kwargs)
    latex_str = latex_str.replace("operator_name", "mathrm")
    plt.text(0.1, 0.1, latex_str, fontsize=20)
    plt.axis('off')
    plt.show()

params = sp.symbols('x0_d0, x0_d1,'
                    ' phi1_d0, phi1_d1,'
                    ' phi2_d0, phi2_d1,'
                    ' m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2')

x0_d0, x0_d1,\
phi1_d0, phi1_d1,\
phi2_d0, phi2_d1,\
m0, m1, m2, l1, l2, F, M1, M2, g, d0, d1, d2 = params

term0 = m0 + m1*sp.sin(phi1_d0)**2 + m2*(sp.sin(phi2_d0))**2
term1 = m1*sp.sin(phi1_d0)*(g*sp.cos(phi1_d0) - l1*phi1_d1**2)
term2 = m2*sp.sin(phi2_d0)*(g*sp.cos(phi2_d0) - l2*phi2_d1**2)

x0_d2 = (term1
         + term2 +
         (F - d0*x0_d1)
         + (M1 - d1*phi1_d1)*sp.cos(phi1_d0)/l1
         + (M2 - d2*phi2_d1)*sp.cos(phi2_d0)/l2) \
        / term0

phi1_d2 = g*sp.sin(phi1_d0)/l1 \
          + sp.cos(phi1_d0)*\
            (term1
             + term2
             + (F - d0*x0_d1)
             + (M1 - d1*phi1_d1)*sp.cos(phi1_d0)/l1
             + (M2 - d2*phi2_d1)*sp.cos(phi2_d0)/l2)\
            /(l1*term0) \
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

# x = sp.Matrix([x0_d0, x0_d1, phi1_d0, phi1_d1, phi2_d0, phi2_d1])
x = sp.Matrix([x0_d0, phi1_d0, phi2_d0, x0_d1, phi1_d1, phi2_d1])  # only for comparison
u = sp.Matrix([F, M1, M2])

# sys = sp.Matrix([x0_d1, x0_d2, phi1_d1, phi1_d2, phi2_d1, phi2_d2])
sys = sp.Matrix([x0_d1, phi1_d1, phi2_d1, x0_d2, phi1_d2, phi2_d2])  # only for comparison

dict_names = {x0_d0: r'x_{0}',
              x0_d1: r'\dot{x}_{0}',
              phi1_d0: r'\varphi_{1}',
              phi1_d1: r'\dot{\varphi}_{1}',
              phi2_d0: r'\varphi_{2}',
              phi2_d1: r'\dot{\varphi}_{2}'}

A = sys.jacobian(x)
A = A.subs([(sp.sin(phi1_d0), 0), (sp.sin(phi2_d0), 0),
            (phi1_d1, 0), (phi2_d1, 0),
            (sp.cos(phi1_d0)**2, 1), (sp.cos(phi2_d0)**2, 1),
            (sp.cos(phi1_d0)**3, sp.cos(phi1_d0)),
            (sp.cos(phi2_d0)**3, sp.cos(phi2_d0))])
# preview(A, mode='equation', mat_str="array", symbol_names=dict_names)
B = sys.jacobian(u)
B = B.subs([(sp.sin(phi1_d0), 0), (sp.sin(phi2_d0), 0),
            (phi1_d1, 0), (phi2_d1, 0),
            (sp.cos(phi1_d0)**2, 1), (sp.cos(phi2_d0)**2, 1),
            (sp.cos(phi1_d0)**3, sp.cos(phi1_d0)),
            (sp.cos(phi2_d0)**3, sp.cos(phi2_d0))])
# preview(B, mode='equation', mat_str="array", symbol_names=dict_names)


