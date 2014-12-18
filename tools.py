# -*- coding: utf-8 -*-
"""
Tools, functions and other funny things
"""
import sympy as sp
import numpy as np

def lieDerivative(h, f, x, n):
    '''
    calculates the Lie-Derivative from a skalarfield h(x) along a vectorfield f(x)
    '''

    if n == 0:
        return h
    elif n == 1:
        return h.jacobian(x) * f
    else:
        return lieDerivative(lieDerivative(h, f, x, 1), f, x, n-1)   
        
def getCoefficients(poles):
    '''
    calculate the coefficient of a characteristic polynom
    '''
    
    s = sp.symbols('s')
    poly = 1    
    for s_i in poles:
        poly = (s-s_i)*poly
    poly = poly.expand()
    
    n = len(poles)
    p = []
    
    # calculate the coefficient of characteristic polynom
    for i in range(n):
        p.append(poly.subs([(s,0)]))
        poly = poly - p[i]
        poly = poly/s
        poly = poly.expand()
        
    return np.array([p]).astype(float)
    
def symMatrixToNumArray(symMatrix = None):
    '''
    convert a sympy Matrix in a numpy array
    '''
    numArray = np.array(symMatrix).astype(float)
    return numArray

    
#print getCoefficients([-2,-2,-2,-2])
#p = getCoefficients([-2,-2,-2,-2])
#print p
#print type(p)
#p = np.array(p).astype(float)
#print p[0]
#print type(p[0])
#matrix = sp.Matrix([[1,2,3,4],[4,5,6,7],[1,2,3,9],[1,8,3,5]])
#print matrix[0,3]
#print type(matrix[0,3])
#
#m = symMatrixToNumArray(matrix)
#print m
#print type(m)
#print type(m[0,3])
