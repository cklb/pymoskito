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
#        t_desired = data['modules']['trajectory']['delta t']
        

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
        #plot y(t)
        axes.plot(t, y, c = 'k', ls='-', label='y(t)')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        axes.legend(loc=4)
        
        #create desired line
        desiredLine = line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)
        

        #calc damping-time (Beruhigungszeit)
        try:                
            eps = self.epsPercent*yd/100
            enterIdx = -1
            for idx, val in enumerate(y):
                if enterIdx == -1:
                    if abs(val - yd) < eps:
                        enterIdx = idx
                else:
                    if abs(val - yd) >= eps:
                        enterIdx = -1
            td = t[enterIdx]
            #create and add line
            self.createTimeLine(axes, t, y, td, r'$T_{\epsilon}$')
            output.update({'td': td})
        except IndexError:
            #print 'DampingLine is not defined'
            output.update({'td': None})
        
        #create epsilon tube
        upperBoundLine = line([0, t[-1]], [yd+eps, yd+eps], ls='--', c=self.line_color)
        axes.add_line(upperBoundLine)
        lowerBoundLine = line([0, t[-1]], [yd-eps, yd-eps], ls='--', c=self.line_color)
        axes.add_line(lowerBoundLine)

        #calc stationary deviation
        ys = y[-1] - yd
        output.update({'ys': ys})
        
        #calc time error
        t_error = (td - t_desired)*t_desired
        print 't_error: ', t_error

        self.calcMetrics(data, output)

        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'A1')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        return canvas
        
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
