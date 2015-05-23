# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import sympy as sp
import numpy as np
import copy


def sort_tree(dataList, sortKeyPath):
    """
    helper method for data sorting
    """
    result = {}
    for elem in dataList:
        tempElem = copy.deepcopy(elem)
        sortName = get_sub_value(tempElem, sortKeyPath)
        if not result.has_key(sortName):
            result.update({sortName: {}})

        while tempElem:
            val, keys = _remove_deepest(tempElem)
            if keys:
                _addSubVal(result[sortName], keys, val)

    return result


def get_sub_value(source, keyPath):
    subDict = source
    for key in keyPath:
        subDict = subDict[key]

    return subDict


def _remove_deepest(topDict, keys=None):
    """
    iterates recursively over dict and removes deepest entry.
    :returns entry and path to entry
    """
    if not keys:
        keys = []

    for key in topDict.keys():
        val = topDict[key]
        if isinstance(val, dict):
            if val:
                keys.append(key)
                return _remove_deepest(val, keys)
            else:
                del topDict[key]
                continue
        else:
            del topDict[key]
            keys.append(key)
            return val, keys

    return None, None


def _addSubVal(topDict, keys, val):
    if len(keys) == 1:
        # we are here
        if keys[0] in topDict:
            topDict[keys[0]].append(val)
        else:
            topDict.update({keys[0]: [val]})
        return

    # keep iterating
    if keys[0] not in topDict:
        topDict.update({keys[0]: {}})

    _addSubVal(topDict[keys[0]], keys[1:], val)
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

