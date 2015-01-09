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
from tools import getSubValue

class eval_L1NormITAE_poles_linePlotClemens(MetaProcessingModule):
    '''
    create diagrams, which plot L1NormITAE over poles
    '''
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #create tree with relevant datas
        source = sortTree(postResults, ['modules', 'controller', 'type'])
        
        # Get the Poles for the Minimum 
        for controller in source:
            xPath=['modules','controller', 'poles']
            yPath=['metrics','L1NormITAE']
            xList = getSubValue(source[controller], xPath)
            yList = getSubValue(source[controller], yPath)
            
            xList[:] = [x for x,y in zip(xList, yList) if y]
            yList[:] = [i for i in yList if i]
            
            print controller
            print '  min ITAE:', min(yList)
            print '  opt poles:', xList[yList.index(min(yList))][0]
            
        
        #create plot
        fig = Figure()
        fig.subplots_adjust(wspace=0.5, hspace=0.25)
        
        #plot for L1NormITAE over poles
        axes = fig.add_subplot(111)
        self.plotVariousController(source, axes,\
                xPath=['modules','controller', 'poles'],\
                yPath=['metrics','L1NormITAE'],\
                typ='line',\
                xIndex = 0)
        self.plotSettings(axes,\
                titel=r'Fehlerintegral ITAE ueber Polplatzierung',\
                grid=True,\
                xlabel=r'$Poles \, \lbrack s\rbrack$',\
                ylabel=r'$E \, \lbrack ms^{2} \rbrack$',\
                )       
        
        #extract controllerNames
        controllerNames = [x[:-len('Controller')] for x in source.keys()]
        
        canvas = FigureCanvas(fig)
        #write output files
        fileName = self.name[len('eval_'):]\
                    + '_Controller_(' + ''.join(controllerNames) + ')'
        self.writeOutputFiles(fileName, fig)
        
        return [{'figure': canvas, 'name': self.name}]
