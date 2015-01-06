# -*- coding: utf-8 -*-
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

class eval_L1NormAbs_delta_t_linePlot(MetaProcessingModule):
    '''
    create diagrams for evaluation of L1NormAbs
    '''
    name = 'eval_L1NormAbs_linePlot'
    
    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def run(self, postResults):
        
        #create dic with relevant datas
        dic = self.createDictionary(postResults)
        
        #create plot
        fig = Figure()
        fig.subplots_adjust(wspace=0.5, hspace=0.25)
        
        #plot for L1NormAbs
        axes = fig.add_subplot(211)
                        
        #plot for time-difference
        axes1 = fig.add_subplot(212)
        
        axes = self.plotVariousController(dic, axes, x='delta_t',y='L1NormAbs', typ='line')
        axes = self.plotSettings(axes,\
                titel=r'Fehlerintegral w(t) und y(t)',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$E \, \lbrack m^{2}\rbrack$',\
                )
        
        axes1 = self.plotVariousController(dic, axes1, x='delta_t',y='t_diff', typ='line')
        axes1 = self.plotSettings(axes1,\
                titel=r'Uebergangszeitfehler ueber $\Delta t$',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$e_{t} \, \lbrack m^{2}\rbrack$',\
                )
        
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', self.name)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, self.name)
        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        fig.savefig(fileName+'.pdf')

        results = [{'figure': canvas, 'name': 'delta_t-line-plot'}]

        return results
