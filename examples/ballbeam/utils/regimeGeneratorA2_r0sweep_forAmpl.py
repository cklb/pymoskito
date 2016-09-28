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

aRange = [0.1, 4.5]
aStepSize = 0.1
freq = 0.1

#####################################################

lines = ''

# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

for contr in controllerList:
    pol = st.poles[contr]
    print(contr)
    print('pol:', pol)
    if contr == 'PIFeedbackController':
        poles = [pol, pol, pol, pol, pol]
    else:
        poles = [pol, pol, pol, pol]
    

    
    As = np.arange(aRange[0],aRange[1] + aStepSize, aStepSize)
    lines += '\n'
    
    for a in As:
            lines += '- name: A2_' + contr + '_f' + str(freq) + '_A'+str(a)+ '\n'
            lines += '  clear previous: !!python/bool False' + '\n'
            lines += '\n'
            lines += '  solver: ' + '\n'
            lines += '   type: VODESolver' + '\n'
            lines += '   initial state: ' + str([a, 0, 0, 0]) + '\n'
            lines += '\n'
            lines += '  controller: ' + '\n'
            lines += '   type: '  + contr + '\n'
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

fileName = 'A2_' +'_f'+str(freq)+ '_r0sweep' + '_all_aRange(' + str(aRange[0])\
            + ',' + str(aRange[1]) + ')'+'.sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
