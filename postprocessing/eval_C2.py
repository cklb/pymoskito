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

class eval_C2(PostProcessingModule):
    '''
    create diagrams for evaluation step C - limitations
    '''

    #padding = .2
    padding = .5
    offset = 0

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    
    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def process(self, dataList):
        print 'process() of C2 called'
        
        output = []
        for cName in st.smoothPoles.keys():
            #check whether controller was in result files
            t = self.extractValues(dataList, [cName, '_unlimited'], 'simTime')
            if not t:
                continue

            print 'found entry of ', cName

            #get curves
            r = [None, None]
            y = [None, None]
            r[0] = self.extractValues(dataList, [cName, '_unlimited'], 'controller_output.0')
            r[1] = self.extractValues(dataList, [cName, '_limited'], 'controller_output.0')
            l = self.extractValues(dataList, [cName, '_limited'], 'limiter_output.0')
            ydes = self.extractValues(dataList, [cName, '_unlimited'], 'trajectory_output.0')
            ydEnd = ydes[-1]
            y[0] = self.extractValues(dataList, [cName, '_unlimited'], 'model_output.0')
            y[1] = self.extractValues(dataList, [cName, '_limited'], 'model_output.0')
            
            #get settings
            limits = self.extractSetting(dataList, [cName, '_limited'], 'limiter', 'limits')
            eps = st.R

            #create plot
            fig = Figure()
            axes = []

            #fig1 controller output
            axes.append(fig.add_subplot(211))
            axes[0].set_title(r'\textbf{Reglerausgaenge im Vergleich}')

            #create limitation tube
            upperBoundLine = line([0, t[-1]], [limits[0]]*2, ls='--', c=self.line_color)
            axes[0].add_line(upperBoundLine)
            lowerBoundLine = line([0, t[-1]], [limits[1]]*2, ls='--', c=self.line_color)
            axes[0].add_line(lowerBoundLine)
            
            axes[0].plot(t, r[0], c='limegreen', ls='-', label='r(t) unlimitriert')
            axes[0].plot(t, r[1], c='indianred', ls='-', label='r(t) limitiert')

            #customize
            axes[0].set_xlim(left=0, right=t[-1])
    #        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
    #                top=(self.offset+yd*(1+self.padding)))

            axes[0].legend(loc=0, fontsize='small')
            axes[0].set_xlabel(r'$t \, \lbrack s \rbrack$')
            axes[0].set_ylabel(r'$\tau \, \lbrack Nm \rbrack$') 

            #fig2 model output
            axes.append(fig.add_subplot(212))
            axes[1].set_title(r'\textbf{Ausgangsverlaeufe im Vergleich}')

            #create epsilon tube
            upperBoundLine = line([0, t[-1]], [ydEnd+eps, ydEnd+eps], ls='--', c=self.line_color)
            axes[1].add_line(upperBoundLine)
            lowerBoundLine = line([0, t[-1]], [ydEnd-eps, ydEnd-eps], ls='--', c=self.line_color)
            axes[1].add_line(lowerBoundLine)
            
            axes[1].plot(t, ydes, c='b', ls='-', label='w(t)')
            axes[1].plot(t, y[0],   c='limegreen', ls='-', label='y(t) unlimitriert')
            axes[1].plot(t, y[1], c='indianred', ls='-', label='y(t) limitiert')

            #customize
            axes[1].set_xlim(left=0, right=t[-1])
    #        axes.set_ylim(bottom=(self.offset+yd*(1-self.padding/2)),\
    #                top=(self.offset+yd*(1+self.padding)))

            axes[1].legend(loc=0, fontsize='small')
            axes[1].set_xlabel(r'$t \, \lbrack s \rbrack$')
            axes[1].set_ylabel(r'$r \, \lbrack m \rbrack$') 

            canvas = FigureCanvas(fig)
        
            # create output files because run is not called
            dataSets = [dataSet for dataSet in dataList if cName in dataSet['regime name']]
            for data in dataSets:
                results = {}
                results.update({'metrics': {} })
                self.calcMetrics(data, results['metrics'])
                
                #add settings and metrics to dictionary results
                results.update({'modules': data['modules']})
                if '_unlimited' in data['regime name']:
                    appendix = '_unlimited'
                else:
                    appendix = '_limited'
                self.writeOutputFiles(self.name, data['regime name'], fig, results)
        

            output.append({'name':'_'.join([cName, self.name]),\
                            'figure': canvas})
        return output
        
    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
        #calc L1NormAbs
        L1NormAbs = self.calcL1NormAbs(data)

        #calc L1NormITAE
        L1NormITAE = self.calcL1NormITAE(data)
        output.update({\
            'L1NormITAE': L1NormITAE,\
            'L1NormAbs': L1NormAbs,\
            })
