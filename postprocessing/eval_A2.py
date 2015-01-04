# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import os

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from postprocessing import PostProcessingModule
import settings as st

#define your own functions here
class eval_A2(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ', data['regime name']
        
        output = {}
        
        # vectorise skalar functions
        vSubt = np.vectorize(self.subt)
        
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
               
        eps = vSubt(y[0], yd)
        
        # plots
        fig = Figure()
#        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes = fig.add_subplot(1, 1, 1)
#        axes.set_title(r'output error = yd - x0')
        axes.plot(t, eps, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'$t /s$')
        axes.set_ylabel(r'$output error = x_{0} - y_{d} /m$')
           
        
        # calculate results
        errorIntegral = self.calcErrorIntegral(data)
        
        output.update({'error_L1Norm': errorIntegral})
        
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'A2')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        return canvas             
        
    def calcErrorIntegral(self, data):
        '''
        calculate metrics for comaprism
        '''

        #calculate datasets
#        t = data['results']['simTime']
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0']

        #calc ITAE criterium
        dt = 1.0/data['modules']['solver']['measure rate']
        
        errorIntegral = 0

        if not data['results']['finished']:       
            errorIntegral = None
        else:
            for k, val in enumerate(y):
                #vgl. Betragskriterium L^1
                errorIntegral += abs(val-yd[k])*dt

        print 'errorIntegral: ', errorIntegral
        return errorIntegral
        

