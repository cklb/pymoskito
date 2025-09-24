"""
This file contains some functions that are quite helpful when designing feedback
laws.
This collection is not complete and does not aim to be so. 
For a more sophisticated collection have a look at the `symbtools`
(https://github.com/TUD-RST/symbtools) or `control` package which are not used
in this package to keep a small footprint.
"""

import warnings
import sympy as sp
import numpy as np
from numpy.linalg import inv as mat_inv

__all__ = ["char_coefficients", "place_siso", "calc_prefilter",
           "controllability_matrix", "observability_matrix",
           "lie_derivatives"
           ]


def lie_derivatives(h, f, x, order=1):
    """
    Calculates the Lie-Derivative from a scalar field :math:`h(x)` along a 
    vector field :math:`f(x)`.
    
    Args:
        h (sympy.matrix): scalar field
        f (sympy.matrix): vector field
        x (sympy.matrix): symbolic representation of the states
        order (int): order

    Return:
        list of sympy.matrix: lie derivatives in ascending order
    """
    derivatives = [h]
    for i in range(order):
        derivatives.append(derivatives[-1].jacobian(x) * f)

    return derivatives


def char_coefficients(poles):
    """
    Calculate the coefficients of a characteristic polynomial.
    
    Args:
        poles (list or :obj:`numpy.ndarray`): pol configuration

    Return:
        :obj:`numpy.ndarray`: coefficients
    """

    poles = np.array(poles)  # convert to numpy array
    poles = np.ravel(poles)  # transform to 1d array

    s = sp.symbols("s")
    poly = 1
    for s_i in poles:
        poly = (s - s_i) * poly
    poly = sp.expand(poly)

    # calculate the coefficient of characteristic polynomial
    n = len(poles)
    p = []
    for i in range(n):
        p.append(poly.subs([(s, 0)]))
        poly = poly - p[i]
        poly = poly / s
        poly = sp.expand(poly)

    # convert numbers and complex objects from multiplication to a complex
    # number
    p = [complex(x) for x in p]

    # if imaginary part is greater than the boundary, set imaginary part to zero
    boundary = 1e-12
    for idx, val in enumerate(p):
        if abs(val.imag) > boundary:
            msg = "Imaginary Part of the coefficient p[{}] "
            "is unequal zero ({})) for a given tolerance of {}".format(
                str(idx), str(boundary), str(val.imag))
            warnings.warn(msg)
        p[idx] = val.real

    return np.array(p, dtype=float)  # [a_0, a_1, ... , a_n-1]


def controllability_matrix(a_mat, b_mat):
    """
    Calculate controllability matrix and check controllability of the system.

    .. math::
        \\boldsymbol{Q_{c}} = \\begin{pmatrix}
        \\boldsymbol{B} & \\boldsymbol{A}\\boldsymbol{B} & \\boldsymbol{A}^{2}
        \\boldsymbol{B} &
        \\cdots & \\boldsymbol{A}^{n-1}\\boldsymbol{B}\\\\
        \\end{pmatrix}

    Args:
        a_mat (:obj:`numpy.ndarray`): system matrix
        b_mat (:obj:`numpy.ndarray`): manipulating matrix

    Return:
        :obj:`numpy.ndarray`: controllability matrix :math:`\\boldsymbol{Q_{c}}`
    """
    a_mat = np.atleast_2d(a_mat)
    b_mat = np.atleast_2d(b_mat)

    # check dimension of matrix A and B
    if a_mat.shape[0] != a_mat.shape[1]:
        raise ValueError("A is not square")
    if a_mat.shape[0] != b_mat.shape[0]:
        raise ValueError("Dimension of A and B does not match")
    if a_mat.shape[0] < b_mat.shape[1]:
        raise ValueError("Dimension of A and B does not match")
    n = a_mat.shape[0]

    # calculate controllability matrix
    qc = b_mat
    for x in range(1, n):
        qc = np.concatenate((qc, np.linalg.matrix_power(a_mat, x) @ b_mat),
                            axis=1)

    # check controllability of the system
    if np.linalg.matrix_rank(qc) != n:
        raise ValueError("System is not controllable")

    return qc


def observability_matrix(a_mat, c_mat):
    """
    Calculate observability matrix and check observability of the system.

    .. math::
        \\boldsymbol{Q_{o}} = \\begin{pmatrix}
        \\boldsymbol{C}\\\\
        \\boldsymbol{C}\\boldsymbol{A}\\\\
        \\boldsymbol{C}\\boldsymbol{A}^{2}\\\\
        \\vdots \\\\
        \\boldsymbol{C}\\boldsymbol{A}^{n-1}\\\\
        \\end{pmatrix}

    Args:
        a_mat (:obj:`numpy.ndarray`): system matrix
        c_mat (:obj:`numpy.ndarray`): output matrix

    Return:
        :obj:`numpy.ndarray`: observability matrix :math:`\\boldsymbol{Q_{o}}`
    """
    a_mat = np.atleast_2d(a_mat)
    c_mat = np.atleast_2d(c_mat)

    # check dimension of matrix A and C
    if a_mat.shape[0] != a_mat.shape[1]:
        raise ValueError("A is not square")
    if a_mat.shape[0] != c_mat.shape[1]:
        raise ValueError("Dimension of A and C does not match")
    if a_mat.shape[0] < c_mat.shape[0]:
        raise ValueError("Dimension of A and C does not match")
    n = a_mat.shape[0]

    # calculate observability matrix
    qo = c_mat
    for x in range(1, n):
        qo = np.concatenate((qo, c_mat @ np.linalg.matrix_power(a_mat, x)),
                            axis=0)

    # check observability of the system
    if np.linalg.matrix_rank(qo) != n:
        raise ValueError("System is not observable")

    return qo


def place_siso(a_mat, b_mat, poles):
    """
    Place poles for single input single output (SISO) systems:

        - pol placement for state feedback: :math:`A` and :math:`b`
        - pol placement for observer: :math:`A^T` and :math:`c`

    Args:
        a_mat (:obj:`numpy.ndarray`): System matrix.:math:`A`
        b_mat (:obj:`numpy.ndarray`): Input vector :math:`b` or Output matrix
            :math:`c` .
        poles (list or :obj:`numpy.ndarray`): Desired poles.

    Return:
        :obj:`numpy.ndarray`: Feedback vector or :math:`k` or observer gain
        :math:`l^T` .
    """

    # check consistency
    if a_mat.shape[0] != a_mat.shape[1]:
        raise ValueError("A is not square")
    n = a_mat.shape[0]
    if n != b_mat.shape[0]:
        raise ValueError("Dimension of A and B does not match")
    m = b_mat.shape[1]
    if m != 1:
        raise ValueError("Dimension of B implies that is not a SISO system")
    if n != len(poles):
        raise ValueError("Dimension of A and the number of poles doesn't match")

    p = char_coefficients(poles)

    # calculate controllability matrix
    q = controllability_matrix(a_mat, b_mat)
    q_inv = np.linalg.inv(q)

    # last row in the inverse controllability matrix
    t1_t = np.atleast_2d(q_inv[-1])

    cm = np.linalg.matrix_power(a_mat, n)
    for i in range(n):
        cm = cm + p[i] * np.linalg.matrix_power(a_mat, i)

    k = np.dot(t1_t, cm)

    return k


def calc_prefilter(a_mat, b_mat, c_mat, k_mat=None):
    """
    Calculate the prefilter matrix

    .. math::
        \\boldsymbol{V} = - \\left[\\boldsymbol{C} \\left(\\boldsymbol{A} -
        \\boldsymbol{B}\\boldsymbol{K}\\right)^{-1}\\boldsymbol{B}\\right]^{-1}

    Args:
        a_mat (:obj:`numpy.ndarray`): system matrix
        b_mat (:obj:`numpy.ndarray`): input matrix
        c_mat (:obj:`numpy.ndarray`): output matrix
        k_mat (:obj:`numpy.ndarray`): control matrix

    Return:
        :obj:`numpy.ndarray`: Prefilter matrix
    """
    a_mat = np.atleast_2d(a_mat)
    b_mat = np.atleast_2d(b_mat)
    c_mat = np.atleast_2d(c_mat)
    k_mat = np.atleast_2d(k_mat)

    # check dimension of matrices A, B and C
    if a_mat.shape[0] != a_mat.shape[1]:
        raise ValueError("A is not square")
    if a_mat.shape[0] != b_mat.shape[0]:
        raise ValueError("Dimension of A and B does not match")
    if a_mat.shape[0] < b_mat.shape[1]:
        raise ValueError("Dimension of A and B does not match")
    if a_mat.shape[0] != c_mat.shape[1]:
        raise ValueError("Dimension of A and C does not match")
    if a_mat.shape[0] < c_mat.shape[0]:
        raise ValueError("Dimension of A and C does not match")

    if k_mat[0, 0] is not None:
        try:
            # prefilter: V = -[C(A-BK)^-1*B]^-1
            v = -mat_inv(c_mat @ (mat_inv(a_mat - b_mat @ k_mat) @ b_mat))
        except np.linalg.linalg.LinAlgError:
            raise ValueError("Cannot calculate V due to singularity.")
    else:
        v = np.array([[1]])

    return v
