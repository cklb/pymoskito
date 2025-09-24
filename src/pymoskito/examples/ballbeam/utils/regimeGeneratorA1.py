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
end_time = 20

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController', 'all']
parameter = 'poles'
#-------------------------------------------------------------
# init
#-------------------------------------------------------------
print('\n ### Regimefile Generator A1 ### \n')

print('Choose controller: ')
for idx, controller in enumerate(controllerList):
    print('\t', idx, ' - ', controller)

controlIdx = -1
while controlIdx not in list(range(0, len(controllerList))):
    controlIdx = eval(input())
    
if controlIdx == len(controllerList)-1:
    simCases = controllerList[:-1]
else:
    simCases = [controllerList[controlIdx]]

#-------------------------------------------------------------
# functions
#-------------------------------------------------------------

#prefined strings
def writeRegime(cName, pole, param, paramVal, appendix):
    return '- name: A1_' + cName + '_poles(' + str(pole) + ')\n'\
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
        tmp += '   r0: 3\n'
    tmp += '\n'
    return tmp

def writeSensor(senName, paramVal):
    return '  sensor:' + '\n'\
            + '   type: ' + senName + '\n'\
            + '   delay: ' + str(paramVal) + '\n'\
            + '   output: ' + '[0,1,2,3]' + '\n\n'

def writeDisturbance(disName, paramVal):
    if paramVal == 0:
        return '  disturbance:' + '\n'\
            + '   type: None\n'

    return '  disturbance:' + '\n'\
            + '   type: ' + disName + '\n'\
            + '   mean value: ' + '0' + '\n'\
            + '   sigma: ' + str(paramVal) + '\n\n'

def saveOutput(output, cName, parameter, limits):
    '''
        wrapper to save regime file
    '''
    dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')

    if not os.path.isdir(dirPath):
        os.makedirs(dirPath)
    
    if cName == 'all':
        fileName = 'A1_' + cName\
                            + '_' + str(parameter)\
                            + '.sreg'
    else:
        fileName = 'A1_' + cName\
                            + '_' + str(parameter)\
                            + '(' + str(simLimits[0]) + ',' + str(simLimits[-1])\
                            + ').sreg'

    filePath = os.path.join(dirPath, fileName)
    with open(filePath, 'w') as f:
        f.write(output)

#-------------------------------------------------------------
# preamble
#-------------------------------------------------------------
preamble = '- name: A1-simulation-setup\n'\
+'  clear previous: !!python/bool True\n'\
+'\n'\
+'  model:\n'\
+'   type: BallBeamModel\n'\
+'\n'\
+'  solver:\n'\
+'   type: VODESolver\n'\
+'   end time: '+str(end_time)+'\n'\
+'\n'\
+'  trajectory:\n'\
+'   type: FixedPointTrajectory\n'\
+'   Position: 3\n'\
+'\n'

#-------------------------------------------------------------
# main
#-------------------------------------------------------------
collection = ''
for controller in simCases:
    lines = preamble

    # how many poles?
    if controller == 'PIFeedbackController':
        multiplicator = 5
    else:
        multiplicator = 4

    #set correct poles
    poles = st.poles[controller]
    
    #get simulation limits
    pole_limits = st.paramPoleVariation[controller]['pole_limits']
    #get simulation step size
    pole_step = st.paramPoleVariation[controller]['pole_step']
    
    #create simulationArray
    simLimits = np.arange(pole_limits[0],\
                            pole_limits[1] - pole_step,\
                            -pole_step)

    #search limits
    for val in simLimits:
        lines += writeRegime(controller, pole=val,\
                            param=None, paramVal=None, appendix=None)
        lines += writeController(controller, val, multiplicator)
        lines += '\n\n'

        saveOutput(lines, controller, parameter, simLimits)

    collection += lines

if len(simCases) > 1:
    saveOutput(collection, 'all', parameter, simLimits)

print('done.')
