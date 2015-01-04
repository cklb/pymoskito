#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']

print 'Regimefile Generator'
print 'Choose one of the following controller: (0-4)'
print controllerList
number = -1
while not(number >= 0 and number <= 4):
    print 'Number: '
    number = input()

print 'Start of poleRange'
start = 1
while not(start >= -100 and start <= 0):
    print 'start: '
    start = input()

print 'End of poleRange'
end = 1
while not(end >= -100 and end <= 0):
    print 'end: '
    end = input()

lines = ''
controller = controllerList[number]
poleRange = [start, end]

if controller == 'PIFeedbackController':
    multiplicator = 5
else:
    multiplicator = 4

# load head file
filePath = os.path.join(os.curdir, 'A1_head.sray')
with open(filePath, 'r') as f:
    head = f.read()


poles = np.arange(poleRange[0],poleRange[1] - 0.1, -0.1)
lines += '\n'

for pole in poles:
        lines += '- name: A1_' + controller + '_poles' + str(pole) + '\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str([pole]*multiplicator) + '\n'
        lines += '\n'

fileName = 'A1_' + controller + '_poleRange(' + str(poleRange[0])\
            + ',' + str(poleRange[1]) + ').sreg'
filePath = os.path.join(os.curdir, fileName)
with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
