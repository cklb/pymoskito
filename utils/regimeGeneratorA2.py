#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']
               
#TODO: überlege, in welchem Punkt Regler linearisiert werden und dazu Pole
number = 0
poles = [-3.6, -3.6, -3.6, -3.6]
fRange = [0.02, 2]
fStepSize = 0.02

lines = ''
controller = controllerList[number]


# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

fs = np.arange(fRange[0],fRange[1] + fStepSize, fStepSize)
lines += '\n'

for f in fs:
        lines += '- name: A2_' + controller + '_f' + str(f) + '\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str(poles) + '\n'
        lines += '\n'
        lines += '  trajectory:' +'\n'
        lines += '   Frequency:' + str(f) + '\n'
        lines += '\n'
               
#write results
#print os.path.pardir
dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'A2_' + controller + '_fRange(' + str(fRange[0])\
            + ',' + str(fRange[1]) + ').sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
