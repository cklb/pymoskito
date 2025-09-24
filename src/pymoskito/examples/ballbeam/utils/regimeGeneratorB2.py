#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
import os

controllerList = ['FController', 'GController', 'JController',\
                'LSSController', 'PIFeedbackController']

print('Regimefile Generator (Modification of M)')
print('Choose one of the following controller: (0-4)')
print(controllerList)
number = -1
while not(number >= 0 and number <= 4):
    print('Number: ')
    number = eval(input())

lines = ''
controller = controllerList[number]


# load head file
filePath = os.path.join(os.curdir, 'B_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

lines += '\n'

# how many poles?
if controller == 'PIFeedbackController':
    multiplicator = 5
else:
    multiplicator = 4


if controller == 'FController':
    pole = -3.6
elif controller == 'GController':
    pole = -3
elif controller == 'JController':
    pole == -2
elif controller == 'LSSController':
    pole = -3.3
elif controller == 'PIFeedbackController':
    pole = -1.5

#M = np.arange(0.03, 0.07, 0.005)
M = np.arange(0.01, 0.2+0.01, 0.01)
    
for m in M:
        lines += '- name: B2_' + controller + '_poles(' + str(pole) \
                    + ')_M(' + str(m) + ')\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  model:' + '\n'
        lines += '   type: BallBeamModel' + '\n'
        lines += '   M: ' + str(m) + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str([pole]*multiplicator) + '\n'
        if (controller == 'PIFeedbackController' or controller == 'LSSController'):
            lines += '   r0: 3'
        lines += '\n'

fileName = 'B2_' + controller + '_poles' + str(pole) \
                    + '_M(' + str(M[0]) + ',' + str(M[-1]) + ').sreg'
filePath = os.path.join(os.curdir, fileName)
with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
