#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------
# trajectory generation
#---------------------------------------------------------------------
def calcTrajectory(t,order):
    '''
    Calculates desired trajectory for ball position
    '''
    #TODO
    A = 1
    #A = 2
    #A = 3
    yd_0 = A * cos(pi*t/5)
    yd_1 = -A * (pi/5) * sin(pi*t/5)
    yd_2 = -A * (pi/5)**2 * cos(pi*t/5)
    yd_3 = A * (pi/5)**3 * sin(pi*t/5)
    yd_4 = A * (pi/5)**4 * cos(pi*t/5)
    yd_derivates = [yd_0 , yd_1 , yd_2 , yd_3 , yd_4]
    yd = []
        
    for i in range(order+1):
        yd.append(yd_derivates[i])
         
    return yd
