# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import os
import settings as st

import matplotlib as mpl
mpl.use("Qt4Agg")
mpl.rcParams['text.usetex']=True
mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessor import PostProcessingModule

#define your own functions here
class eval_A1_steps_in_one_plot(PostProcessingModule):
    '''
    create several step respond in one plot
    '''

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2./5
    spacing = 0.01
    counter = 0
    
    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def process(self, files):
        
          
        print 'processing ', self.name
        
        #reset counter
        self.counter = 0
        
        #dict for calculated values
#        output = {}
        yd = 0
        

            
        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'Sprungantworten')
        #search t max
        t_max = 0
        for data in files:
            t = data['modules']['solver']['end time']
            if t > t_max:
                t_max = t
        axes.set_xlim(left=0, right=t_max)
        axes.set_ylim(0,4,5)
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        
        controllerName = []
        #create plots
        counter = 0
        for data in files:
#            print data['modules']
#            print data['regime name']
#            print data['results']['finished']
            #calculate datasets
            t = data['results']['simTime']
            y = data['results']['model_output.0']
            yd = data['results']['trajectory_output.0'][-1]
            controllerName.append(data['modules']['controller']['type'])
            axes.plot(t, y, label=r'$r_{0} = ' + str(data['modules']['controller']['r0']) + '$',\
                            c=mpl.rcParams['axes.color_cycle'][counter])
            counter += 1
            
            
            
            
            #check for sim succes
#            if not data['results']['finished']:
#                for key in output.keys():
#                    output[key] = None

#        self.posLabel = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)
        
        #plot legend
        axes.legend()        
        
        #create desired line
        desiredLine = line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)

        
        
        #create epsilon tube
        upperBoundLine = line([0, t[-1]], [yd+st.R, yd+st.R], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = line([0, t[-1]], [yd-st.R, yd-st.R], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)
        
#        #calc control deviation
#        control_deviation = y[-1] - yd
#        output.update({'control_deviation': control_deviation})

#        self.calcMetrics(data, output)


        #add settings and metrics to dictionary results
        results = {}
#        results.update({'metrics': output})
#        results.update({'modules': data['modules']})
        
        canvas = FigureCanvas(fig)
    
        self.writeOutputFiles(self.name, 'steps_in_one_plot', fig, results)

        return [{'name':'_'.join([controllerName[0], self.name]),\
                    'figure': canvas}]
        

    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
        
        L1NormITAE = self.calcL1NormITAE(data)            
        L1NormAbs = self.calcL1NormAbs(data)
#                    
#        print 'ITAE score: ', errorIntegral
        print 'L1NormITAE: ', L1NormITAE
        print 'L1NormAbs: ', L1NormAbs
        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})
#        output.update({'ITAE': errorIntegral})
