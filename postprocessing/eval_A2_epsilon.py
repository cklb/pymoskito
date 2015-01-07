# -*- coding: utf-8 -*-
import numpy as np

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from postprocessor import PostProcessingModule

#define your own functions here
class eval_A2_epsilon(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''
    name = 'A2_epsilon'    
    
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
               
        error = np.subtract(y[0], yd)
        output.update({'error': error})
        
        # plots
        fig = Figure()
        #fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes = fig.add_subplot(1, 1, 1)
        #axes.set_title(r'output error = yd - x0')
        axes.plot(t, error, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'$t [s]$')
        axes.set_ylabel(r'$output error = x_{0} - y_{d} [m]$')
           
        # calculate L1NormAbs
        L1NormAbs = self.calcL1NormAbs(data)
        output.update({'L1NormAbs': L1NormAbs})
        
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