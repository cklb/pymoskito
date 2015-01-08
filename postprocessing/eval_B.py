# -*- coding: utf-8 -*-
import numpy as np
import os

from operator import itemgetter

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessor import PostProcessingModule
import settings as st

#define your own functions here
class eval_B(PostProcessingModule):
    '''
    create diagrams for evaluation step B
    '''

    name = 'B'
    #padding = .2
    padding = .5
    offset = 0

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5
    #spacing = 0.01
    #counter = 0
    
    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def process(self, dataList):
        print 'process() of B called'
        output = {}
        
        #ideal regime name
        regName = next((result['regime name']\
                for result in dataList if 'ideal' in result['regime name']), None)

        #extract the needed curves
        t = self.extractValues(dataList, 'ideal', 'simTime')
        y_ideal = self.extractValues(dataList, 'ideal', 'model_output.0')
        y_desired = self.extractValues(dataList, 'ideal', 'trajectory_output.0')
        yd = y_desired[-1]
        y_pTolMin = self.extractValues(dataList, 'paramTolMin', 'model_output.0')
        y_pTolMax = self.extractValues(dataList, 'paramTolMax', 'model_output.0')

        par = next((param for param in st.paramVariationListB if param in regName), None)
        print 'assuming that', par, 'has been varied.'

        #sort files by variied parameter
        modDataList = sorted(dataList, key=lambda k: k['modules']['model'][par], reverse=False)

        #find minimal stable iteration
        resAbsMin = next((res \
                for res in modDataList if res['results']['finished']), None)
        y_pAbsMin = resAbsMin['results']['model_output.0']

        #find maximum stable iteration
        resAbsMax = next((res \
                for res in reversed(modDataList) if res['results']['finished']), None)
        y_pAbsMax = resAbsMax['results']['model_output.0']
        #print len(y_pAbsMin), len(y_pAbsMax), len(y_ideal)

        print 'stablity limits are:',\
                resAbsMin['modules']['model'][par], '/', resAbsMax['modules']['model'][par]
        
        output.update({'parameter': par,\
                'minLimit': resAbsMin['modules']['model'][par],\
                'maxLimit': resAbsMax['modules']['model'][par],\
                })

        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Vergleich Signalverlaeufe}')

        #create epsilon tub
        eps = self.epsPercent*yd/100
        upperBoundLine = line([0, t[-1]], [yd+eps, yd+eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = line([0, t[-1]], [yd-eps, yd-eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)
        
        #create signals
        axes.add_line(lowerBoundLine)
        axes.plot(t, y_ideal,   c='k', ls='-', label='parameter ideal')
        axes.plot(t, y_desired, c='b', ls='-', label='w(t)')
        axes.plot(t, y_pTolMin, c='c', ls='-', label='unteres Toleranzlimit')
        axes.plot(t, y_pTolMax, c='lime', ls='-', label='oberes Toleranzlimit')
        axes.plot(t, y_pAbsMin, c='orange', ls='-', label='untere Stabilitaetsgrenze')
        axes.plot(t, y_pAbsMax, c='r', ls='-', label='obere Stabilitaetsgrenze')


        #customize
        axes.set_xlim(left=0, right=t[-1])
#        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
#                top=(self.offset+yd*(1+self.padding)))

        axes.legend(loc=0, fontsize='small')

        canvas = FigureCanvas(fig)
        
        # create output files because run is not called
        for data in dataList:
            results = {}
            results.update({'metrics': {} })
            self.calcMetrics(data, results['metrics'])
            
            #add settings and metrics to dictionary results
            results.update({'modules': data['modules']})
            self.writeOutputFiles(self.name, data['regime name'], fig, results)
        
        results = {'metrics': output}
        self.writeOutputFiles(self.name, regName[:-len('ideal')] + 'paramLimits', None, results)
        
        return [{'name':'_'.join([regName[:-len('ideal')], 'paramLimits', self.name]),\
                    'figure': canvas}]
        
    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''

        #calc L1NormITAE
        L1NormITAE = self.calcL1NormITAE(data)
        output.update({'L1NormITAE': L1NormITAE})
