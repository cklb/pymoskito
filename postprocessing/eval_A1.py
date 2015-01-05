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
from matplotlib.lines import Line2D as line

from postprocessor import PostProcessingModule

#define your own functions here
class eval_A1(PostProcessingModule):
    '''
    create diagrams for evaluation step A1
    '''

    name = 'A1'

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
        yd = data['results']['trajectory_output.0'][-1]

        self.posLabel = np.arange(np.min(y) + 0.1*yd, yd, (yd-np.min(y))/4)
            
        #create plot
        fig = Figure()
        axes = fig.add_subplot(111)
        axes.set_title(r'\textbf{Sprungantwort}')
        axes.plot(t, y, c='k')
        axes.set_xlim(left=0, right=t[-1])
        axes.set_xlabel(r'\textit{Zeit [s]}')
        axes.set_ylabel(r'\textit{Ballposition r(t) [m]}')
        
        #create desired line
        desiredLine = line([0, t[-1]], [yd, yd], lw=1, ls=self.line_style, c='k')
        axes.add_line(desiredLine)

        #calc rise-time (Anstiegszeit)
        try:            
            tr = t[y.index([x for x in y if x > yd*0.9][0])]
            #create and add line
            self.createTimeLine(axes, t, y, tr, r'$T_r$')
            output.update({'tr': tr})
        except IndexError:
            output.update({'tr': None})
            #print 'AttackLine is not defined'
        
        #calc correction-time (Anregelzeit)
        try:
            tanr = t[y.index([x for x in y if x > yd][0])]
            #create and add line
            self.createTimeLine(axes, t, y, tanr, r'$T_{anr}$')
            output.update({'tanr': tanr})
        except IndexError:
            #print 'RiseLine is not defined'
            output.update({'tanr': None})
        
        #calc overshoot-time and overshoot in percent (Überschwingzeit und Überschwingen)
        if output['tanr']:
            if yd > 0:
                y_max = np.max(y[t.index(tanr):])
            else:
                y_max = np.min(y[t.index(tanr):])
#            lastval = 0
#            for val in y[t.index(tanr):]:
#                y_max = (val - yd)*yd
                
#                if val < lastval:
#                    break
#                else:
#                    lastval = val
            to = t[y.index(y_max)]
#            to = t[y.index(val)]
            do = y_max - yd
            doPercent = do/yd * 100
            #create and add line
            self.createTimeLine(axes, t, y, to, r'$T_m$')
            output.update({'to': to, 'do': do, 'doPercent': doPercent})
        else:
            #print 'OvershootLine is not defined'
            output.update({'to': None, 'do': None, 'doPercent': None})

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

        self.calcMetrics(data, output)
        #copy module settings to output
        output.update({'modules':data['modules']})

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
                            [np.min(y), y[t.index(time_value)]],\
                            ls = self.line_style,\
                            c = self.line_color) 
            axes.add_line(timeLine)
            #create label
            axes.text(time_value + self.spacing,\
                        self.posLabel[self.counter],\
                        label,\
                        size = self.font_size)
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
        if not data['results']['finished']:
            errorIntegral = None
        else:
            for k, val in enumerate(y):
                errorIntegral += abs(val-yd)*dt**2*k
                    
        print 'ITAE score: ', errorIntegral
        output.update({'ITAE': errorIntegral})
