# -*- coding: utf-8 -*-
import numpy as np

import matplotlib as mpl
mpl.use("Qt4Agg")
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processing_gui import PostProcessingModule

#define your own functions here
class eval_C_observer(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''
    line_color = '#aaaaaa'
    line_style = '-'

    name = 'C_observer'

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
        xm = []
        xo = []
        e = []
        for i in range(4):
            xm.append(data['results']['model_output.'+str(i)])
            xo.append(data['results']['observer_output.'+str(i)])
            e.append(vSubt(xo[i],xm[i]))
               
        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)
    
        axes = []
        for i in range(4):
            axes.append(fig.add_subplot(5, 1, i+1))
            axes[i].plot(t, xo[i], c='b', ls = '-', label = 'xo['+str(i)+']')
            axes[i].plot(t, xm[i], c='k', ls = '-', label = 'xm['+str(i)+']')
            axes[i].set_xlim(left=0, right=t[-1])
            
        axes.append(fig.add_subplot(5, 1, 5))
        leg = []
        for i in range(4):
            axes[4].plot(t, e[i], ls = '-', label = 'e['+str(i)+']')
            leg.append('e['+str(i)+']')
            
        axes[4].legend(leg, loc = 0, fontsize = 'small')
              
        # calculate results
        # L1 
        dt = 1.0/data['modules']['solver']['measure rate']
        errorIntegrals = [0,0,0,0]
        
        #check for sim succes
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None
        
        for i in range(len(errorIntegrals)):
            for k, val in enumerate(xo[i]):
                #vgl. Betragskriterium L^1
                errorIntegrals[i] +=1
                errorIntegrals[i] += abs(val-xm[i][k])*dt
    
            print 'errorIntegral_x['+str(i)+']:', errorIntegrals[i]
            output.update({'error_L1Norm_x['+str(i)+']': errorIntegrals[i]})


        #add settings and metrics to dictionary results
        results = {}
        results.update({'metrics': output})
        results.update({'modules': data['modules']})
        
        canvas = FigureCanvas(fig)
        
        self.writeOutputFiles(self.name, data['regime name'], fig, results)

        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}
    
        

