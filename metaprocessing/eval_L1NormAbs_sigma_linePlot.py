# -*- coding: utf-8 -*-
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
mpl.rcParams['text.usetex']=True
mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from postprocessor import MetaProcessingModule
from tools import sortTree

class eval_L1NormAbs_sigma_linePlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of L1NormAbs
    '''
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #create tree with relevant datas
        source = sortTree(postResults, ['modules', 'controller', 'type'])
        
        #create plot
        fig = Figure()
        fig.subplots_adjust(wspace=0.5, hspace=0.25)
        
        #plot for L1NormAbs
        axes = fig.add_subplot(111)
                        
        self.plotVariousController(source, axes,\
                xPath=['modules', 'disturbance', 'sigma'],\
                yPath=['metrics', 'L1NormAbs'],\
                typ='line')
        self.plotSettings(axes,\
                titel=r'Fehlerintegral w(t) und y(t) \"uber Sigma',\
                grid=True,\
                xlabel=r'$\sigma \, \lbrack m\rbrack$',\
                ylabel=r'$E \, \lbrack ms \rbrack$',\
                )
        
        #extract controllerNames
        controllerNames = [x[:-len('Controller')] for x in source.keys()]
        
        canvas = FigureCanvas(fig)
        #write output files
        fileName = self.name[len('eval_'):]\
                    + '_Controller_(' + ''.join(controllerNames) + ')'
        self.writeOutputFiles(fileName, fig)
        
        return [{'figure': canvas, 'name': self.name}]
