# -*- coding: utf-8 -*-

#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processing_gui import MetaProcessingModule
from tools import sortTree


class eval_L1NormAbs_delta_t_linePlot(MetaProcessingModule):
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
        
        #plot for L1NormAbs
        axes = fig.add_subplot(211)
        self.plotVariousController(source, axes,\
                xPath=['modules','trajectory', 'delta t'],\
                yPath=['metrics','L1NormAbs'],\
                typ='line')
        self.plotSettings(axes,\
                titel=r'Fehlerintegral w(t) und y(t) \"uber $\Delta t$',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$E \, \lbrack ms\rbrack$',\
                )
                        
        #plot for time-difference
        axes1 = fig.add_subplot(212)
        self.plotVariousController(source, axes1,\
                xPath=['modules','trajectory', 'delta t'],\
                yPath=['metrics','t_diff'],\
                typ='line')
        self.plotSettings(axes1,\
                titel=r'\"Ubergangszeitfehler \"uber $\Delta t$',\
                grid=True,\
                xlabel=r'$\Delta t \, \lbrack s\rbrack$',\
                ylabel=r'$e_{t} \, \lbrack s\rbrack$',\
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
