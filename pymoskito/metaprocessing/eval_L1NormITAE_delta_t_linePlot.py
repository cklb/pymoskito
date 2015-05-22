# -*- coding: utf-8 -*-
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from postprocessor import MetaProcessingModule
from tools import sortTree

class eval_L1NormITAE_delta_t_linePlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of L1NormITAE
    '''
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #create tree with relevant datas
        source = sortTree(postResults, ['modules', 'controller', 'type'])
        
        #create plot
        fig = Figure()
        
        #plot for L1NormITAE
        axes = fig.add_subplot(211)
        self.plotVariousController(source, axes,\
                xPath=['modules','trajectory', 'delta t'],\
                yPath=['metrics','L1NormITAE'],\
                typ='line')
        self.plotSettings(axes,\
                titel=r'Fehlerintegral ITAE w(t) und y(t) \"uber $\Delta t$',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$E \, \lbrack ms^{2} \rbrack$',\
                )       
        
        #plot for time-difference
        axes1 = fig.add_subplot(212)
        axes1 = self.plotVariousController(source, axes1,\
                xPath=['modules','trajectory', 'delta t'],\
                yPath=['metrics','t_diff'],\
                typ='line')
        axes1 = self.plotSettings(axes1,\
                titel=r'\"Ubergangszeitfehler \"uber $\Delta t$',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$e_{t} \, \lbrack s \rbrack$',\
                )
        
        # spacing
        fig.subplots_adjust(wspace=0.5, hspace=0.5)

        #extract controllerNames
        controllerNames = [x[:-len('Controller')] for x in source.keys()]
        
        canvas = FigureCanvas(fig)
        #write output files
        fileName = self.name[len('eval_'):]\
                    + '_Controller_(' + ''.join(controllerNames) + ')'
        self.writeOutputFiles(fileName, fig)
        
        return [{'figure': canvas, 'name': self.name}]
