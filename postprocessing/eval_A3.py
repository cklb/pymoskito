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

from postprocessor import PostProcessingModule

#define your own functions here
class eval_A3(PostProcessingModule):
    '''
    create diagrams for evaluation step A3
    '''

    name = 'A3'

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5
    spacing = 0.01
    counter = 0
    
    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ',data['regime name']

        #dict for calculated values
        output = {}

        #reset counter
        self.counter = 0
        
        #calculate datasets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        traj = data['results']['trajectory_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        self.posLabel = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)
            
        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Vergleich Signalverlaeufe (Systemantwort und Trajektorie)}')
        axes.plot(t, traj, c='b', ls='-', label='w(t)')
        #create t_desired line
        #search time value for t_desired
        t_desired = t[traj.index(yd)]
        self.createTimeLine(axes, t, traj, t_desired, r'$T_{des}$')
        # add real t_desired to dict output
        output.update({'t_desired': data['modules']['trajectory']['delta t']})
        #plot y(t)
        axes.plot(t, y, c = 'k', ls='-', label='y(t)')
        # axes scaling
        axes.set_xlim(left=0, right=t[-1])
        y_min = np.min(y)
        y_max = np.max(y)
        if (np.max(y) == 0):
            axes.set_ylim(np.min(traj), np.max(traj) + np.max(traj)*0.1)
        else:
            axes.set_ylim(y_min, y_max + y_max*0.1)
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        axes.legend(loc=4)
        
        #create desired line
        desiredLine = line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)
        

        #calc damping-time (Beruhigungszeit)
        eps = self.epsPercent*yd/100
        enterIdx = -1
        for idx, val in enumerate(y):
            if enterIdx == -1:
                if abs(val - yd) < eps:
                    enterIdx = idx
            else:
                if abs(val - yd) >= eps:
                    enterIdx = -1
        if enterIdx == -1:
            #print 'DampingLine is not defined'
            output.update({'td': None})
        else:
            td = t[enterIdx]
            #create and add line
            self.createTimeLine(axes, t, y, td, r'$T_{\epsilon}$')
            output.update({'td': td})

        
        #create epsilon tube
        upperBoundLine = line([0, t[-1]], [yd+eps, yd+eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = line([0, t[-1]], [yd-eps, yd-eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)

        #calc stationary deviation
        ys = y[-1] - yd
        output.update({'ys': ys})

        self.calcMetrics(data, output)

        #check for sim sucess
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None
    
        #copy module settings to output
        output.update({'modules':data['modules']})
        
        print output
        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', self.name)
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}
        
    def createTimeLine(self, axes, t, y, time_value, label):
        if time_value != t[-1]:
            #create timeLine
            timeLine = line([time_value, time_value],\
                            [axes.get_ylim()[0], y[t.index(time_value)]],\
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
        traj = data['results']['trajectory_output.0']
        delta_t = data['modules']['trajectory']['delta t']

        #calc ITAE criterium and Error
        dt = 1.0/data['modules']['solver']['measure rate']
        integralError = 0
        integralITAE = 0
        
        if not data['results']['finished']:
            integralError = None
            integralITAE = None
        else:
            for index, val in enumerate(y):
                integralITAE += abs(val-yd)*dt**2*index
                integralError += abs(val - traj[index])
               
        print 'ITAE score: ', integralITAE
        print 'integralError', integralError
        
        # calculate time difference
        if output['td'] == None:
            t_diff = None
        else:
            t_diff = output['td'] - data['modules']['trajectory']['delta t']
        
        
        output.update({ 'delta_t': delta_t,\
                        'ITAE': integralITAE,\
                        'integralError': integralError,\
                        't_diff': t_diff })
