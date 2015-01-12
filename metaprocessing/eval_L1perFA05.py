# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import os
import settings as st

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessor import MetaProcessingModule

class eval_L1perFA05(MetaProcessingModule):
    '''
    create diagrams for evaluation of itea metric
    '''

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5
    spacing = 0.01
    counter = 0
    
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return
        
    def sortLists(self, val):
        val[1] = [x for (y, x) in sorted(zip(val[0], val[1]))]
        val[0] = sorted(val[0])
        return val
        

    def run(self, postResults):
        controllerDict = {'FController': [[],[]],\
                          'GController': [[],[]],\
                          'JController': [[],[]],\
                          'LSSController': [[],[]],\
                          'PIFeedbackController': [[],[]]}
                          
        # TODO: levels per input füllen
        level1 = 'modules'
        level2 = 'trajectory'
        level3 = 'Frequency'
        xLabel = 'f [Hz]'
        yLabel = 'E [m^2]'
                          
        for elem in postResults:
            controllerDict[elem['modules']['controller']['type']][0].append(elem[level1][level2][level3])
            controllerDict[elem['modules']['controller']['type']][1].append(elem['metrics']['L1NormAbs'])
            
        fig = Figure()
        axes = fig.add_subplot(1, 1, 1)
        
        xMax = 0
        leg = []
        for elem in controllerDict:
            controllerDict[elem] = self.sortLists(controllerDict[elem])
            axes.plot(controllerDict[elem][0], controllerDict[elem][1],\
                       ls='-', c=st.color_cycle[elem])
            leg.append(elem)
            if controllerDict[elem][0]:
                if xMax < controllerDict[elem][0][-1]:
                    xMax = controllerDict[elem][0][-1]       
        axes.legend(leg, loc=1)
        axes.set_xlim(left=0.1, right=xMax)
#        axes.set_ylim(top=6.0, bottom=3)
        axes.set_xlabel(r'$'+xLabel+'$', size=st.label_size)
        axes.set_ylabel(r'$'+yLabel+'$', size=st.label_size) 
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A2')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        metaName = 'L1-plotFA05'
        fileName = os.path.join(filePath, metaName)
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        fig.savefig(fileName+'.png')
        fig.savefig(fileName+'.pdf')

        results = [{'figure': canvas, 'name': metaName},\
                ]

        return results
