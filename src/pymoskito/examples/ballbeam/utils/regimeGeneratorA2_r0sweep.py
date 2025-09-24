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

fRange = [0.05, 0.2]
fStepSize = 0.01
ampl = 3

#####################################################
lines = ''

# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

for contr in controllerList:
    # Pole festlegen nach A1
    pol = st.poles[contr]
    print(contr)
    print('pol:', pol)
    
    if contr == 'PIFeedbackController':
        poles = [pol, pol, pol, pol, pol]
    else:
        poles = [pol, pol, pol, pol]
    
    
    
    fs = np.arange(fRange[0],fRange[1] + fStepSize, fStepSize)
    lines += '\n'
    
    for f in fs:
            lines += '- name: A2_' + contr + '_A' + str(ampl) + '_f' + str(f) + '\n'
            lines += '  clear previous: !!python/bool False' + '\n'
            lines += '\n'
            lines += '  solver: ' + '\n'
            lines += '   type: VODESolver' + '\n'
            lines += '   initial state: ' + str([ampl, 0, 0, 0]) + '\n'
            lines += '\n'
            lines += '  controller: ' + '\n'
            lines += '   type: '  + contr + '\n'
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

fileName = 'A2_' + '_A('+str(ampl)+')_r0sweep' + '_all_fRange(' + str(fRange[0])\
            + ',' + str(fRange[1]) + ')'+'.sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
