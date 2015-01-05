# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessor import MetaProcessingModule

class eval_itae(MetaProcessingModule):
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

    def run(self, postResults):
        #aquire data
        errors = [elem['ITAE'] for elem in postResults]
        poles = [elem['modules']['controller']['poles'] for elem in postResults]

        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{ITAE Kriterium}')
        axes.plot(poles, errors, c='k')
        #axes.set_xlim(left=0, right=t[-1])
        #axes.set_xlabel(r'\textit{Zeit [s]}')
        #axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A1')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, 'ITEA-plot')
        canvas = FigureCanvas(fig)
#        fig.savefig(fileName+'.svg')
        fig.savefig(fileName+'.png')

        results = [{'figure': canvas, 'name': 'ITEA-plot'},\
                ]

        return results
