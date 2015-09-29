# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import os
import sympy as sp
import numpy as np
import copy


def sort_lists(a, b):
    b = [x for (y, x) in sorted(zip(a, b))]
    a = sorted(a)
    return a, b


def get_resource(res_name):
    """
    find path to specified resource
    :param res_name: resource
    :return: path to resource
    """
    own_path = os.path.dirname(__file__)
    resource_path = os.path.abspath(os.path.join(own_path, "data"))
    return os.path.join(resource_path, res_name)


def sort_tree(data_list, sort_key_path):
    """
    helper method for data sorting.

    takes a list of simulation results and sorts them into a tree whose index is given by the sort_key_path
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
    """
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

    return np.array([p]).astype(float)
