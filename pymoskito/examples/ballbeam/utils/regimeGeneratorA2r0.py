#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os
import settings as st

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']
               
#TODO: überlege, in welchem Punkt Regler linearisiert werden und dazu Pole
#####################################################
# Einstellungen               
number = 2

fRange = [0.1, 0.6]
fStepSize = 0.05
ampl = 0.5

#####################################################
lines = ''
controller = controllerList[number]

# Pole festlegen nach A1
pol = st.poles[controllerList[number]]
print(controller)
print('pol:', pol)

if controller == 'PIFeedbackController':
    poles = [pol, pol, pol, pol, pol]
else:
    poles = [pol, pol, pol, pol]

# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

fs = np.arange(fRange[0],fRange[1] + fStepSize, fStepSize)
lines += '\n'

for f in fs:
        lines += '- name: A2_' + controller + '_A' + str(ampl) + '_f' + str(f) + '\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str(poles) + '\n'
        lines += '\n'
        lines += '  trajectory:' +'\n'
        lines += '   type: HarmonicTrajectory' + '\n'
        lines += '   Amplitude: ' + str(ampl) + '\n'
        lines += '   Frequency: ' + str(f) + '\n'
        lines += '\n'
               
#write results
#print os.path.pardir
dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'A2_' + controller + '_A'+str(ampl)+'_fRange(' + str(fRange[0])\
            + ',' + str(fRange[1]) + ')'+'.sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
