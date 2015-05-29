# -*- coding: utf-8 -*-
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
mpl.rcParams['text.usetex']=True
mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from processing_gui import MetaProcessingModule
import settings as st
from tools import sortTree

class eval_L1Norms_param_linePlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of integralError
    '''
    name = 'eval_L1_over_param'
    
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #create tree with relevant data
        source = sortTree(postResults, ['modules', 'controller', 'type'])

        #get ideal regime name
        fileName = postResults[0]['name']

        #extract parameter that has been varied
        param = next((param for param in st.paramVariationListB\
                if '_'+param+'(' in fileName),\
                None)
        print 'assuming that', param, 'has been varied.'

        #create plot
        figs = []
        figs.append(Figure())
        figs.append(Figure())
        
        #plot for L1NormAbs
        axes = []
        axes.append(figs[0].add_subplot(111))
        axes.append(figs[1].add_subplot(111))
        
        self.plotVariousController(source, axes[0],\
                xPath=['modules','model', param],\
                yPath=['metrics','L1NormAbs'],\
                typ='line')

        if param == 'M':
            xlbl=r'$M \, \lbrack kg\rbrack$'
        elif param == 'J':
            xlbl=r'$M \, \lbrack kg\rbrack$'
        else:
            xlbl = ''

        self.plotSettings(axes[0],\
                titel=u'Fehlerintegral',\
                grid=True,\
                xlabel=xlbl,\
                ylabel=r'$E \, \lbrack ms\rbrack$',\
                )
        self.plotVariousController(source, axes[1],\
                xPath=['modules','model', param],\
                yPath=['metrics','L1NormITAE'],\
                typ='line')

        self.plotSettings(axes[1],\
                titel=u'ITAE Fehler',\
                grid=True,\
                xlabel=xlbl,\
                ylabel=r'$E \, \lbrack ms^2\rbrack$',\
                )
                        
        #extract controllerNames
        controllerNames = [x[:-len('Controller')] for x in source.keys()]
        
        canvas = []
        canvas.append(FigureCanvas(figs[0]))
        canvas.append(FigureCanvas(figs[1]))

        #write output files
        fileName = self.name[len('eval_'):]\
                    + '_Controller_(' + ''.join(controllerNames) + ')'

        names = []
        names.append('_'.join([fileName, param, 'Abs']))
        names.append('_'.join([fileName, param, 'ITAE']))

        self.writeOutputFiles(names[0], figs[0])
        self.writeOutputFiles(names[1], figs[1])
        
        return [\
                {'figure': canvas[0], 'name': names[0]},\
                {'figure': canvas[1], 'name': names[1]},\
                ]

