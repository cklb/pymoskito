# -*- coding: utf-8 -*-
import numpy as np
import os

controller = 'FController'
poleRange = [-1,-10]

lines = ''
poles = np.arange(poleRange[0],poleRange[1],-0.1)
for pole in poles:
        lines += '- name: A1-FController_poles' + str(pole) + '\n'
        lines += '  clear previous: !!python/bool False' + '\n'
        lines += '\n'
        lines += '  controller: ' + '\n'
        lines += '   type: '  + controller + '\n'
        lines += '   poles: ' + str([pole]*4) + '\n'
        lines += '\n'

fileName = 'regGen_poleRange.sray'
filePath = os.path.join(os.curdir, fileName)
with open(filePath, 'w') as f:
    f.write(lines)
