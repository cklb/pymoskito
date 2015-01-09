# -*- coding: utf-8 -*-
import numpy as np
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line
import settings as st

from postprocessor import PostProcessingModule

#define your own functions here
class eval_A2(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''
    line_color = '#aaaaaa'
    line_style = '-'

    name = 'A2'

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ', data['regime name']
        
        output = {}
        
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
               
        eps = np.subtract(y[0], yd)
        traj = data['results']['trajectory_output.0']
        
        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)
        fig.suptitle(r'\textbf{' + data['modules']['controller']['type'] + ' '+\
                     'A_d=' + str(data['modules']['trajectory']['Amplitude'])+ ' '+\
                     'f_d=' + str(data['modules']['trajectory']['Frequency']) + '}',\
                     size=st.title_size)
    
        axes1 = fig.add_subplot(2, 1, 1)
        #axes2.set_title(r'\textbf{Beam Angle}')
        axes1.plot(t, traj, c='k', ls='-', label='yd(t)')
        axes1.plot(t, y[0], c = st.color_cycle[data['modules']['controller']['type']],\
                   ls='-', label='y(t)')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t [s]$', size=st.label_size)
        axes1.set_ylabel(r'$r [m]$', size=st.label_size)
        leg = [r'$y_d(t)$', r'$y(t)$']
        axes1.legend(leg, loc=0)
        
        axes2 = fig.add_subplot(2, 1, 2)
#        axes.set_title(r'output error = yd - x0')        
#        deltaE = 0.01
#        eMax = line([0, t[-1]], [deltaE, deltaE], lw=1,\
#                            ls='--', c=self.line_color)
#        eMin = line([0, t[-1]], [-deltaE, -deltaE], lw=1,\
#                            ls='--', c=self.line_color)        
#        axes2.add_line(eMax)
#        axes2.add_line(eMin)
        
        axes2.plot(t, eps, c='k')
        axes2.set_xlim(left=0, right=t[-1])
#        axes2.set_ylim(top=0.4, bottom=-0.4)
        axes2.set_xlabel(r'$t [s]$', size=st.label_size)
        axes2.set_ylabel(r'$output error = x_{0} - y_{d} [m]$', size=st.label_size) 
        
        self.calcMetrics(data, output)

        #check for sim succes
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None
        
        #add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})
        
        canvas = FigureCanvas(fig)
        
        self.writeOutputFiles(self.name, data['regime name'], fig, results)
        
        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}
        
    def calcMetrics(self, data, output):
        '''
        calculate metrics for comaprism
        '''
         
        L1NormITAE = self.calcL1NormITAE(data)            
        L1NormAbs = self.calcL1NormAbs(data)

        print 'L1NormITAE: ', L1NormITAE
        print 'L1NormAbs: ', L1NormAbs
        
        output.update({'L1NormITAE': L1NormITAE, 'L1NormAbs': L1NormAbs})
        

