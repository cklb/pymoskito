# -*- coding: utf-8 -*-
import os
import settings as st

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from postprocessor import MetaProcessingModule

class eval_L1NormAbs_delta_t_barPlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of L1NormAbs
    '''
    name = 'eval_L1NormAbs_barPlot'
    
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        #create dic with relevant datas
        dic = self.createDictionary(postResults)
        
        #create plot
        fig = Figure()
        
        #plot for L1NormAbs
        axes = fig.add_subplot(111)
        
        axes = self.plotVariousController(dic, axes, x='delta_t',y='L1NormAbs', typ='bar')
        axes = self.plotSettings(axes,\
                titel=r'Fehlerintegral w(t) und y(t)',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$E \, \lbrack m^{2}\rbrack$',\
                )
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A1')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, self.name)
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')

        results = [{'figure': canvas, 'name': 'delta_t-bar-plot'}]

        return results
