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

from postprocessor import PostPostProcessingModule

class eval_L1perF(PostPostProcessingModule):
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
        PostPostProcessingModule.__init__(self)
        return
        
    def sortLists(self, val):
        val['e'] = [x for (y, x) in sorted(zip(val['x'], val['e']))]
        val['x'] = sorted(val['x'])
        return val
        

    def run(self, postResults):
        F = {'x':[], 'e':[]}
        G = {'x':[], 'e':[]}
        J = {'x':[], 'e':[]}
        LSS = {'x':[], 'e':[]}
        PIF = {'x':[], 'e':[]}
        controllerList = ['FController',\
                          'GController',\
                          'JController',\
                          'LSSController',\
                          'PIFeedbackController']
        # TODO: levels per input füllen
        level1 = 'modules'
        level2 = 'trajectory'
        level3 = 'Frequency'
        xLabel = 'f [Hz]'
        yLabel = 'E [m^2]'
                          
        for elem in postResults:
            if elem['modules']['controller']['type']==controllerList[0]: 
                F['x'].append(elem[level1][level2][level3])    
                F['e'].append(elem['error_L1Norm'])
            if elem['modules']['controller']['type']==controllerList[1]:
                G['x'].append(elem[level1][level2][level3])    
                G['e'].append(elem['error_L1Norm'])
            if elem['modules']['controller']['type']==controllerList[2]:
                J['x'].append(elem[level1][level2][level3])    
                J['e'].append(elem['error_L1Norm'])
            if elem['modules']['controller']['type']==controllerList[3]:
                LSS['x'].append(elem[level1][level2][level3])    
                LSS['e'].append(elem['error_L1Norm'])
            if elem['modules']['controller']['type']==controllerList[4]:
                PIF['x'].append(elem[level1][level2][level3])    
                PIF['e'].append(elem['error_L1Norm'])
        
        #listen sortieren
#        F['e'] = [x for (y, x) in sorted(zip(F['x'], F['e']))]
#        F['x'] = sorted(F['x'])
        F = self.sortLists(F)
        G = self.sortLists(G)
        J = self.sortLists(J)
        LSS = self.sortLists(LSS)
        PIF = self.sortLists(PIF)
        
        #fMax = max(F['x'][-1]), G['x'][-1], J['x'][-1], LSS['x'][-1], PIF['x'][-1])
        fMax = F['x'][-1]
        fig = Figure()
        
        axes = fig.add_subplot(1, 1, 1)
        #axes2.set_title(r'\textbf{Beam Angle}')
        axes.plot(F['x'], F['e'], c='b', ls='-')
        axes.plot(G['x'], G['e'], c='b', ls='-')
        axes.plot(J['x'], J['e'], c='b', ls='-')
        axes.plot(LSS['x'], LSS['e'], c='b', ls='-')
        axes.plot(PIF['x'], PIF['e'], c='b', ls='-')
        
        axes.set_xlim(left=0, right=fMax)
        axes.set_xlabel(r'$'+xLabel+'$')
        axes.set_ylabel(r'$'+yLabel+'$') 
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postpostprocessing', 'A2')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, 'L1-plot')
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')

        results = [{'figure': canvas, 'name': 'L1-plot'},\
                ]

        return results
