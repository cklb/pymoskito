#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

import sys
sys.path.append(os.path.pardir)

import settings as st
#-------------------------------------------------------------
# settings
#-------------------------------------------------------------
scale = 2

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']

#-------------------------------------------------------------
# init
#-------------------------------------------------------------
print '\n ### Regimefile Generator Eval C ### \n'

print 'Choose parameter to test: '
for idx, param in enumerate(st.paramVariationListC):
    print '\t',idx,' - ', param

paramIdx = -1
while paramIdx not in range(0, len(st.paramVariationListC)):
    paramIdx = input()

# extract parameter values
parameter = st.paramVariationListC[paramIdx]
lower_bound = st.paramVariationDictC[parameter]['lower_bound']
upper_bound = st.paramVariationDictC[parameter]['upper_bound']
step_size = st.paramVariationDictC[parameter]['step_size']

print 'Choose controller: '
for idx, controller in enumerate(controllerList):
    print '\t',idx,' - ', controller

controlIdx = -1
while controlIdx not in range(0, len(controllerList)):
    controlIdx = input()

controller = controllerList[controlIdx]

# how many poles?
if controller == 'PIFeedbackController':
    multiplicator = 5
else:
    multiplicator = 4

#set correct poles
pole = st.poles[controller]

# load head file
filePath = os.path.join(os.curdir, 'C_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

lines = '\n'

#-------------------------------------------------------------
# functions
#-------------------------------------------------------------

#prefined strings
def writeRegime(cName, pole, param, paramVal, appendix):
    return '- name: C_' + cName + '_poles(' + str(pole) + ')'\
                    + '_' + parameter +'(' + str(paramVal) + ')'\
                    + appendix + '\n'\
                    + '  clear previous: !!python/bool False \n\n'

def writeModel(param, paramVal):
    return '  model:' + '\n'\
            + '   type: BallBeamModel' + '\n'\
            + '   ' + parameter + ': ' + str(paramVal) + '\n\n'

def writeController(cName, pole, multiplicator):
    tmp = '  controller: ' + '\n'\
            + '   type: '  + controller + '\n'\
            + '   poles: ' + str([pole]*multiplicator) + '\n'

    if (controller == 'PIFeedbackController' or controller == 'LSSController'):
        tmp += '   r0: 3'
    tmp += '\n'
    return tmp

def writeSensor(senName, paramVal):
    return '  sensor:' + '\n'\
            + '   type: ' + senName + '\n'\
            + '   delay: ' + str(paramVal) + '\n'\
            + '   output: ' + '[0,1,2,3]' + '\n\n'

def writeDisturbance(disName, paramVal):
    return '  disturbance:' + '\n'\
            + '   type: ' + disName + '\n'\
            + '   mean value: ' + '0' + '\n'\
            + '   sigma: ' + str(paramVal) + '\n\n'

#-------------------------------------------------------------
# main
#-------------------------------------------------------------
simLimits = np.arange(lower_bound, upper_bound + step_size, step_size)

#search limits
for val in simLimits:
    lines += writeRegime(controller, pole, parameter, val, '')
    lines += writeController(controller, pole, multiplicator)
    if parameter == 'sigma':
        lines += writeDisturbance('GaussianNoiseDisturbance', val)
    if parameter == 'delay':
        lines += writeSensor('DeadTimeSensor', val)   


dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')

if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'C_' + controller + '_poles' + str(pole) \
                    + '_' + str(parameter)\
                    + '(' + str(simLimits[0]) + ',' + str(simLimits[-1])\
                    + ').sreg'

filePath = os.path.join(dirPath, fileName)
with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
print 'done.'
