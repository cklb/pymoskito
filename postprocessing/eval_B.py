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
    padding = .2
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
        print 'assuiming that', par, 'has been varied.'

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
        print len(y_pAbsMin), len(y_pAbsMax), len(y_ideal)

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
        axes.plot(t, y_pTolMax, c='g', ls='-', label='oberes Toleranzlimit')
        axes.plot(t, y_pAbsMin, c='orange', ls='-', label='untere Stabilitaetsgrenze')
        axes.plot(t, y_pAbsMax, c='r', ls='-', label='obere Stabilitaetsgrenze')


        #customize
        axes.set_xlim(left=0, right=t[-1])
        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
                top=(self.offset+yd*(1+self.padding)))

        axes.legend(loc=0, fontsize='small')
         
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', self.name)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, regName)
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        
        result = [\
                {'name': '_'.join([regName, self.name]), 'figure': canvas},\
                ]
        return result
        
    def createTimeLine(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            #create timeLine
            timeLine = line([time_value, time_value],\
                            [np.min(y), y[t.index(time_value)]],\
                            ls = self.line_style,\
                            c = self.line_color) 
            axes.add_line(timeLine)
            #create label
            axes.text(time_value + self.spacing, self.posLabel[self.counter], label, size = self.font_size)
            self.counter = self.counter + 1

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''

        #calculate datasets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        #calc ITAE criterium
        dt = 1.0/data['modules']['solver']['measure rate']
        
        errorIntegral = 0
#        if 'finished' in data['results']:
#            if not data['results']['finished']:
#                errorIntegral = None
#            else:
#                for k, val in enumerate(y):
#                    errorIntegral += abs(val-yd)*dt**2*k

        for k, val in enumerate(y):
            errorIntegral += abs(val-yd)*dt**2*k
        print 'ITAE score: ', errorIntegral
        output.update({'ITAE': errorIntegral})
