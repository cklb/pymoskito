#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

observerList = ['LuenbergerObserver', 'HighGainObserver']
               
number = 1

#poles = [pol, pol, pol, pol]
pRange = [50, 2000]
pStepSize = 50
observer = observerList[number]

lines = ''



# load head file
filePath = os.path.join('A2_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

pList= np.arange(pRange[0],pRange[1] + pStepSize, pStepSize)
lines += '\n'

for pol in pList:
    poles = [-pol, -pol, -pol, -pol]
    lines += '- name: C_' + observer + '_pol' + str(pol) + '\n'
    lines += '  clear previous: !!python/bool False' + '\n'
    lines += '\n'
    lines += '  solver:' + '\n'
    lines += '   type: VODESolver' + '\n'
    lines += '   initial state: [-4, 4.91768866, -0.2, -0.7]' + '\n'
    lines += '  controller: ' + '\n'
    lines += '   type: None\n'
    lines += '   poles: ' + str(poles) + '\n'
    lines += '\n'
    lines += '  trajectory:' +'\n'
    lines += '   type: HarmonicTrajectory' + '\n'
    lines += '   Amplitude: 1' + '\n'
    lines += '   Frequency: 1' + '\n'
    lines += '\n'
    lines += '  observer:' + '\n'    
    lines += '   type: '+ observer +'\n'
    lines += '   tick divider: 1' +'\n'
    lines += '   poles: ' + str(poles)+'\n'
    lines += '   initial state: [0, 0, 0, 0]'+'\n'
    if observer == 'LuenbergerObserver':
        lines += '   lin state: [0, 0, 0, 0]' +'\n'
    lines += '\n'                                        
            
#write results
#print os.path.pardir
dirPath = os.path.join(os.path.pardir, os.path.pardir, 'regimes', 'generated')
if not os.path.isdir(dirPath):
    os.makedirs(dirPath)

fileName = 'C2_' + observer +'_pol' + '_pRange(' + str(pRange[0])\
            + ',' + str(pRange[1]) + ')'+'.sreg'
            
filePath = os.path.join(dirPath, fileName)   

with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
    
    
    
    
