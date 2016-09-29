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
scale = 100 #in % of param ideal value

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']

#-------------------------------------------------------------
# init
#-------------------------------------------------------------
print('\n ### Regimefile Generator Eval B ### \n')

print('Choose parameter to test: ')
for idx, param in enumerate(st.paramVariationListB):
    print('\t', idx, ' - ', param)

paramIdx = -1
while paramIdx not in list(range(0, len(st.paramVariationListB))):
    paramIdx = eval(input())

parameter = st.paramVariationListB[paramIdx]
tol = st.paramToleranceList[paramIdx]

paramRealValue = getattr(st, parameter)
paramTolMinValue = paramRealValue - paramRealValue*tol
paramTolMaxValue = paramRealValue + paramRealValue*tol
paramMinValue = paramRealValue - paramRealValue*tol

print('Choose controller: ')
for idx, controller in enumerate(controllerList):
    print('\t', idx, ' - ', controller)

controlIdx = -1
while controlIdx not in list(range(0, len(controllerList))):
    controlIdx = eval(input())

controller = controllerList[controlIdx]

# how many poles?
if controller == 'PIFeedbackController':
    multiplicator = 5
else:
    multiplicator = 4

#set correct poles
pole = st.poles[controller]

#load head file
filePath = os.path.join(os.curdir, 'B_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

lines = '\n'

#-------------------------------------------------------------
# functions
#-------------------------------------------------------------

#prefined strings
def writeRegime(cName, pole, param, paramVal, appendix):
    return '- name: B_' + cName + '_poles(' + str(pole) + ')'\
                    + '_' + parameter +'(' + str(paramVal) + ')'\
                    + '_' + appendix + '\n'\
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

#-------------------------------------------------------------
# main
#-------------------------------------------------------------
#ideal regime
lines += writeRegime(controller, pole, parameter, paramRealValue, 'ideal')
lines += writeModel(parameter, paramRealValue)
lines += writeController(controller, pole, multiplicator)

#tolerance bounds
lines += writeRegime(controller, pole, parameter, paramTolMinValue, 'paramTolMin')
lines += writeModel(parameter, paramTolMinValue)
lines += writeController(controller, pole, multiplicator)
lines += writeRegime(controller, pole, parameter, paramTolMaxValue, 'paramTolMax')
lines += writeModel(parameter, paramTolMaxValue)
lines += writeController(controller, pole, multiplicator)

paramBounds = st.paramStabilityLimits[controller][parameter]
simLimits = np.arange(paramBounds[0], paramBounds[1], paramRealValue/scale)

#iterate between limits
#for val in simLimits:
    #lines += writeRegime(controller, pole, parameter, val, 'paramAbs')
    #lines += writeModel(parameter, val)
    #lines += writeController(controller, pole, multiplicator)

dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'B_' + controller + '_poles' + str(pole) \
                    + '_' + str(parameter)\
                    + '(' + str(simLimits[0]) + ',' + str(simLimits[-1])\
                    + ').sreg'

filePath = os.path.join(dirPath, fileName)
with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)

print('done.')
