#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']
               
#TODO: überlege, in welchem Punkt Regler linearisiert werden und dazu Pole
number = 4
#pol = -3.6
#pol = -3
#pol = -2
#pol = -3.3
pol = -1.5

#poles = [pol, pol, pol, pol]
aRange = [0.1, 3]
aStepSize = 0.1
freq = 0.1

lines = ''
controller = controllerList[number]

if controller == 'PIFeedbackController':
    poles = [pol, pol, pol, pol, pol]
else:
    poles = [pol, pol, pol, pol]

# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

As = np.arange(aRange[0],aRange[1] + aStepSize, aStepSize)
lines += '\n'

for a in As:
        lines += '- name: A2_' + controller + '_f' + str(freq) + '_A'+str(a)+ '\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str(poles) + '\n'
        lines += '\n'
        lines += '  trajectory:' +'\n'
        lines += '   type: HarmonicTrajectory' + '\n'
        lines += '   Amplitude: ' + str(a) + '\n'
        lines += '   Frequency: ' + str(freq) + '\n'
        lines += '\n'
               
#write results
#print os.path.pardir
dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'A2_' + controller +'_f'+str(freq)+ '_aRange(' + str(aRange[0])\
            + ',' + str(aRange[1]) + ')'+'.sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
