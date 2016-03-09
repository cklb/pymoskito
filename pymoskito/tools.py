# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import os
import sympy as sp
import numpy as np
import copy
import warnings


def sort_lists(a, b):
    b = [x for (y, x) in sorted(zip(a, b))]
    a = sorted(a)
    return a, b


def get_resource(res_name, res_type="icons"):
    """
    build absolute path to specified resource within the package

    :param res_name: resource
    :param res_type: subdir
    :return: path to resource
    """
    own_path = os.path.dirname(__file__)
    resource_path = os.path.abspath(os.path.join(own_path, os.pardir, "resources", res_type))
    return os.path.join(resource_path, res_name)


def sort_tree(data_list, sort_key_path):
    """
    helper method for data sorting.

    takes a list of simulation results and sorts them into a tree whose index is given by the sort_key_path

    :param data_list:
    :param sort_key_path:
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
    iterates recursively over dict and removes deepest entry.
    :returns entry and path to entry
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


def lie_derivative(h, f, x, n):
    """
    calculates the Lie-Derivative from a scalar field h(x) along a vector field f(x)
    """
    if n == 0:
        return h
    elif n == 1:
        return h.jacobian(x) * f
    else:
        return lie_derivative(lie_derivative(h, f, x, 1), f, x, n - 1)


def get_coefficients(poles):
    """
    calculate the coefficient of a characteristic polynomial
    :param poles: list or numpy array with poles
    :return: coefficients as a 2d numpy array (row vector)
    """

    poles = np.array(poles)
    s = sp.symbols('s')
    poly = 1
    for s_i in poles:
        poly = (s - s_i) * poly
    poly = poly.expand()

    # calculate the coefficient of characteristic polynomial
    n = len(poles)
    p = []
    for i in range(n):
        p.append(poly.subs([(s, 0)]))
        poly = poly - p[i]
        poly = poly / s
        poly = poly.expand()

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

    return np.array([p], dtype=float)


def rotation_matrix_xyz(axis, angle, angle_dim):
    """
    calculate the rotation matrix for a rotation around
    a given axis with the angle phi
    :param axis: rotation axis
    :param angle: rotation angle
    :param angle_dim: angle dimensions, options: rad, deg
    :return: rotation_matrix
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
    rotation_matrix = np.array([[c + x**2*(1 - c), x*y*(1 - c) - z*s, x*z*(1 - c) + y*s],
                                [y*x*(1 - c) + z*s, c + y**2*(1 - c), y*z*(1 - c) - x*s],
                                [z*x*(1 - c) - y*s, z*y*(1 - c) + x*s, c + z**2*(1 - c)]])

    return rotation_matrix

def controlability_matrix(A, B):
    """
    calculate controlability matrix and check controlability of the system
    :param A:
    :param B:
    :return:
    """

    # check dimension of matrix A and B
    if A.shape[0] != A.shape[1]:
        raise ValueError('A is not square')
    if A.shape[0] != B.shape[0]:
        raise ValueError('Dimension of A and B does not match')
    n = A.shape[0]

    # calculate controlability matrix
    Qc = B
    for x in range(1,n):
        Qc = np.concatenate((Qc, np.dot(np.linalg.matrix_power(A, x), B)), axis=1)

    # check controlability of the system
    if np.linalg.matrix_rank(Qc) != n:
        raise ValueError('System is not controllable')

    return Qc


def ackerSISO(A, B, poles):
    """
    place poles and return a numpy row-matrix
   - place poles for a state feedback: you have to not transpose A and B
   - place poles for a observer: you have to transpose A and C,
     you will get a transposed L
    :param A:
    :param B:
    :param poles:
    :return:
    """

    #check consistency
    if A.shape[0] != A.shape[1]:
        raise ValueError('A is not square')
    n = A.shape[0]
    if n != B.shape[0]:
        raise ValueError('Dimension of A and B does not match')
    m = B.shape[1]
    if m != 1:
        raise ValueError('Dimension of B implies that is not a SISO system')
    if n != len(poles):
        raise ValueError('Dimension of A and the number of poles does not match')

    p = get_coefficients(poles)

    # calculate controlability matrix
    Q = controlability_matrix(A, B)
    Q_inv = np.linalg.inv(Q)

    # last row in the inverse controlability matrix
    t1T = np.atleast_2d(Q_inv[-1])

    cm = np.linalg.matrix_power(A, n)
    for i in range(n):
        cm = cm + p[0][i] * np.linalg.matrix_power(A, i)

    K = np.dot(t1T, cm)

    return K


def calc_prefilter(A, B, C, K=None):
    """
    calculate the prefilter and return a float
    :param A:
    :param B:
    :param C:
    :param K:
    :return:
    """
    # prefilter: V = -[C(A-BK)^-1*B]^-1
    if K is not None:
        try:
            V = - np.linalg.inv(np.dot(np.dot(C, np.linalg.inv(A - np.dot(B, K))), B))
        except np.linalg.linalg.LinAlgError:
            print 'Can not calculate V, because of a Singular Matrix'
            V = np.array([[1]])
    else:
        V = np.array([[1]])

    return V