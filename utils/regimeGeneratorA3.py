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

lines = ''
controller = controllerList[number]


# load head file
filePath = os.path.join(os.curdir, 'A3_head.sray')
with open(filePath, 'r') as f:
    head = f.read()

delta_t = np.arange(11, 21, 1)
#delta_t = np.arange(0.1, 1, 0.1)
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

    
for t in delta_t:
        lines += '- name: A3_' + controller + '_poles(' + str(pole) \
                    + ')_delta_t(' + str(t) + ')\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  trajectory:' + '\n'
        lines += '   type: SmoothTransitionTrajectory' + '\n'
        lines += '   Positions: [0, 3]' + '\n'
        lines += '   start time: 0' + '\n'
        lines += '   delta t: ' + str(t) + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str([pole]*multiplicator) + '\n'
        if (controller == 'PIFeedbackController' or controller == 'LSSController'):
            lines += '   r0: 3'
        lines += '\n'

fileName = 'A3_' + controller + '_poles' + str(pole) \
                    + '_delta_t(' + str(delta_t[0]) + ',' + str(delta_t[-1]) + ').sreg'
filePath = os.path.join(os.curdir, fileName)
with open(filePath, 'w') as f:
    f.write(head)    
    f.write(lines)
