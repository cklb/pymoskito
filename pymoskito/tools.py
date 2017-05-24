# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import copy
import logging
import os
import re
import warnings

import numpy as np
from numpy.linalg import inv as mat_inv
import sympy as sp
from PyQt5.QtWidgets import QPlainTextEdit

logger = logging.getLogger(__name__)

__all__ = ["calc_prefilter", "place_siso", "get_coefficients"
           "controlability_matrix", "observability_matrix",
           "rotation_matrix_xyz", "get_resource"
           "lie_derivatives"]


def sort_lists(a, b):
    b = [x for (y, x) in sorted(zip(a, b))]
    a = sorted(a)
    return a, b


def get_resource(res_name, res_type="icons"):
    """
    Build absolute path to specified resource within the package

    Args:
        res_name (str): name of the resource
        res_type (str): subdir

    Return:
        str: path to resource
    """
    own_path = os.path.dirname(__file__)
    resource_path = os.path.abspath(os.path.join(own_path, "resources", res_type))
    return os.path.join(resource_path, res_name)


def sort_tree(data_list, sort_key_path):
    """
    Helper method for data sorting.
    Takes a list of simulation results and sorts them into a tree whose index is given by the sort_key_path

    Args:
        data_list (list): list of simulation results
        sort_key_path (str):

    Return:
        dict: sorted dictionary
    """
    result = {}
    for elem in data_list:
        temp_element = copy.deepcopy(elem)
        sort_name = get_sub_value(temp_element, sort_key_path)
        if sort_name not in result:
            result.update({sort_name: {}})

        while temp_element:
            val, keys = _remove_deepest(temp_element)
            if keys:
                _add_sub_value(result[sort_name], keys, val)

    return result


def get_sub_value(source, key_path):
    sub_dict = source
    for key in key_path:
        sub_dict = sub_dict[key]

    return sub_dict


def _remove_deepest(top_dict, keys=None):
    """
    Iterates recursively over dict and removes deepest entry.

    Args:
        top_dict (dict): dictionary
        keys (list): select entries to remove

    Return:
        tuple: entry and path to entry
    """
    if not keys:
        keys = []

    for key in top_dict.keys():
        val = top_dict[key]
        if isinstance(val, dict):
            if val:
                keys.append(key)
                return _remove_deepest(val, keys)
            else:
                del top_dict[key]
                continue
        else:
            del top_dict[key]
            keys.append(key)
            return val, keys

    return None, None


def _add_sub_value(top_dict, keys, val):
    if len(keys) == 1:
        # we are here
        if keys[0] in top_dict:
            top_dict[keys[0]].append(val)
        else:
            top_dict.update({keys[0]: [val]})
        return

    # keep iterating
    if keys[0] not in top_dict:
        top_dict.update({keys[0]: {}})

    _add_sub_value(top_dict[keys[0]], keys[1:], val)
    return


def lie_derivatives(h, f, x, order=1):
    """
    Calculates the Lie-Derivative from a scalar field :math:`h(x)` along a 
    vector field :math:`f(x)`.
    
    Todo:
        Move this to a control related module, for the long shot, replace
        with implementation from pycontroltools.

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


def get_coefficients(poles):
    """
    Calculate the coefficients of a characteristic polynomial.
    
    Todo:
        Move this to a control related module

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
        # poly = s**n + a_n-1*s**(n-1) + ... + a_1*s + a_0

    # convert numbers and complex objects from multiplication to a complex number
    p = [complex(x) for x in p]
    # if imaginary part if greater than the boundary, then set imaginary part null
    boundary = 1e-12
    for idx, val in enumerate(p):
        val = complex(val)
        if abs(val.imag) > boundary:
            msg = "Imaginary Part of the coefficient p[" + \
                  str(idx) + "] is not null (" + str(val.imag) + ") for a given boundary of " + \
                  str(boundary)
            warnings.warn(msg)
        p[idx] = val.real

    return np.array([p], dtype=float)  # [a_0, a_1, ... , a_n-1]


def rotation_matrix_xyz(axis, angle, angle_dim):
    """
    Calculate the rotation matrix for a rotation around a given axis with the angle :math:`\\varphi`.

    Args:
        axis (str): choose rotation axis "x", "y" or "z"
        angle (int or float): rotation angle :math:`\\varphi`
        angle_dim (str): choose "deg" for degree or "rad" for radiant

    Return:
        :obj:`numpy.ndarray`: rotation matrix
    """
    assert angle_dim is "deg" or angle_dim is "rad"
    assert axis is "x" or axis is "y" or axis is "z"
    x = 0
    y = 0
    z = 0

    if angle_dim is "deg":
        a = np.deg2rad(angle)
    else:
        a = angle

    if axis is "x":
        x = 1
        y = 0
        z = 0
    if axis is "y":
        x = 0
        y = 1
        z = 0
    if axis is "z":
        x = 0
        y = 0
        z = 1

    s = np.sin(a)
    c = np.cos(a)
    rotation_matrix = np.array([[c + x ** 2 * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                                [y * x * (1 - c) + z * s, c + y ** 2 * (1 - c), y * z * (1 - c) - x * s],
                                [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z ** 2 * (1 - c)]])
    return rotation_matrix


def controlability_matrix(A, B):
    """
    Calculate controlability matrix and check controlability of the system.

    .. math::
        \\boldsymbol{Q_{c}} = \\begin{pmatrix}
        \\boldsymbol{B} & \\boldsymbol{A}\\boldsymbol{B} & \\boldsymbol{A}^{2}\\boldsymbol{B} &
        \\cdots & \\boldsymbol{A}^{n-1}\\boldsymbol{B}\\\\
        \\end{pmatrix}

    Args:
        A (:obj:`numpy.ndarray`): system matrix
        B (:obj:`numpy.ndarray`): manipulating matrix

    Return:
        :obj:`numpy.ndarray`: controlability matrix :math:`\\boldsymbol{Q_{c}}`
    """
    A = np.atleast_2d(A)
    B = np.atleast_2d(B)

    # check dimension of matrix A and B
    if A.shape[0] != A.shape[1]:
        raise ValueError("A is not square")
    if A.shape[0] != B.shape[0]:
        raise ValueError("Dimension of A and B does not match")
    if A.shape[0] < B.shape[1]:
        raise ValueError("Dimension of A and B does not match")
    n = A.shape[0]

    # calculate controlability matrix
    Qc = B
    for x in range(1, n):
        Qc = np.concatenate((Qc, np.dot(np.linalg.matrix_power(A, x), B)), axis=1)

    # check controlability of the system
    if np.linalg.matrix_rank(Qc) != n:
        raise ValueError("System is not controllable")

    return Qc


def observability_matrix(A, C):
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
        A (:obj:`numpy.ndarray`): system matrix
        C (:obj:`numpy.ndarray`): output matrix

    Return:
        :obj:`numpy.ndarray`: observability matrix :math:`\\boldsymbol{Q_{o}}`
    """
    A = np.atleast_2d(A)
    C = np.atleast_2d(C)

    # check dimension of matrix A and C
    if A.shape[0] != A.shape[1]:
        raise ValueError("A is not square")
    if A.shape[0] != C.shape[1]:
        raise ValueError("Dimension of A and C does not match")
    if A.shape[0] < C.shape[0]:
        raise ValueError("Dimension of A and C does not match")
    n = A.shape[0]

    # calculate observability matrix
    Qo = C
    for x in range(1, n):
        Qo = np.concatenate((Qo, C @ np.linalg.matrix_power(A, x)), axis=0)

    # check controlability of the system
    if np.linalg.matrix_rank(Qo) != n:
        raise ValueError("System is not observable")

    return Qo


def place_siso(A, B, poles):
    """
    Place poles for single input single output (SISO) systems:

        - pol placement for state feedback: A and B
        - pol placement for observer: transpose A and C, you will get a transposed gain matrix

    Args:
        A (:obj:`numpy.ndarray`): system matrix.
        B (:obj:`numpy.ndarray`): manipulating matrix.
        poles (list or :obj:`numpy.ndarray`): desired poles.

    Return:
        :obj:`numpy.ndarray`: control matrix.
    """

    # check consistency
    if A.shape[0] != A.shape[1]:
        raise ValueError("A is not square")
    n = A.shape[0]
    if n != B.shape[0]:
        raise ValueError("Dimension of A and B does not match")
    m = B.shape[1]
    if m != 1:
        raise ValueError("Dimension of B implies that is not a SISO system")
    if n != len(poles):
        raise ValueError("Dimension of A and the number of poles does not match")

    p = get_coefficients(poles)

    # calculate controllability matrix
    Q = controlability_matrix(A, B)
    Q_inv = np.linalg.inv(Q)

    # last row in the inverse controllability matrix
    t1T = np.atleast_2d(Q_inv[-1])

    cm = np.linalg.matrix_power(A, n)
    for i in range(n):
        cm = cm + p[0][i] * np.linalg.matrix_power(A, i)

    K = np.dot(t1T, cm)

    return K


def calc_prefilter(a_mat, b_mat, c_mat, k_mat=None):
    """
    Calculate the prefilter matrix

    .. math::
        \\boldsymbol{V} = - \\left[\\boldsymbol{C} \\left(\\boldsymbol{A} -
        \\boldsymbol{B}\\boldsymbol{K}\\right)^{-1}\\right]^{-1}

    Args:
        a_mat (:obj:`numpy.ndarray`): system matrix
        b_mat (:obj:`numpy.ndarray`): manipulating matrix
        c_mat (:obj:`numpy.ndarray`): output matrix
        k_mat (:obj:`numpy.ndarray`): control matrix

    Return:
        :obj:`numpy.ndarray`: prefilter matrix
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
            v = -mat_inv(c_mat @ (mat_inv(a_mat - b_mat * k) @ b_mat))
        except np.linalg.linalg.LinAlgError:
            raise ValueError("Can not calculate V, due to singular matrix")
    else:
        v = np.array([[1]])

    return v


class QPlainTextEditLogger(logging.Handler):
    """
    Logging handler that displays log-data in the gui
    """
    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        # self.widget.setStyleSheet(
        #     """ QLineEdit { background-color: grey} """
        # )

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class PostFilter(logging.Filter):
    """
    Filter to sort out all not PostProcessing related log information
    """
    def __init__(self, invert=False):
        logging.Filter.__init__(self)
        self._invert = invert
        self.exp = re.compile(r"Post|Meta|Process")

    def filter(self, record):
        m = self.exp.match(record.name)
        if self._invert:
            return not bool(m)
        else:
            return bool(m)
