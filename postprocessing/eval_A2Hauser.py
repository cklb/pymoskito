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
from matplotlib.figure import Figure

from postprocessor import PostProcessingModule
import settings as st

#define your own functions here
class eval_A2Hauser(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    name = 'A2_hauser'

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        print 'processing ', data['regime name']
        
        # vectorise skalar functions
        vSubt = np.vectorize(self.subt)
        vMul = np.vectorize(self.mul)
        vAdd = np.vectorize(self.add)
        vDiv = np.vectorize(self.div)
          
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
            
        eps = vSubt(y[0], yd)
        
        # controlleroutput is a torque
        tau = data['results']['controller_output.0']
        # u in the neglected nonlinearity is theta_dd
        u = vDiv(vSubt(vSubt(tau,\
                             np.dot(np.dot(np.dot(2*st.M, y[0]), y[1]), y[3])),\
                             np.dot(st.M*st.G, np.cos(y[2]))),\
                 vAdd(vAdd(np.dot(st.M, np.power(y[0], 2)), st.J), st.Jb))
        
        # Parameter from Controller -> make modelling (estimate/meausre paramters)
        # and then neglect psi therm
        # you are interested in the error through the negligence 
        B = st.B
        G = st.G

        
        if data['modules']['controller']['type'] == 'FController':
            psi = vMul(np.dot(B, y[0]), np.power(y[3],2))
        elif data['modules']['controller']['type'] == 'GController':
            psi = vMul(vMul(np.dot(2*B, y[0]), y[3]), u)
        elif data['modules']['controller']['type'] == 'JController':
            psi = vAdd(vMul(np.dot(B,y[0]), np.power(y[3], 2)),\
                       np.dot(B*G, vSubt(y[2], np.sin(y[2]))))
        else:
            print 'psi is useless'
            psi = np.dot(0, t)

        # plots
        fig = Figure()
        #fig.tight_layout()
        #fig.subplots_adjust(left=0.1, right=1.3, top=1.3, bottom=0.1)
        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes1 = fig.add_subplot(2, 2, 1)
        #axes1.set_title(r'\textbf{output error = yd - x0}')
        axes1.plot(t, eps, c='k')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t /s$')
        axes1.set_ylabel(r'$e /m$')
        
        axes2 = fig.add_subplot(2, 2, 2)
        #axes2.set_title(r'\textbf{Beam Angle}')
        axes2.plot(t, y[2], c='k')
        axes2.set_xlim(left=0, right=t[-1])
        axes2.set_xlabel(r'$t /s$')
        axes2.set_ylabel(r'$\theta$')
            
        
        axes3 = fig.add_subplot(2, 2, 3)
        #axes3.set_title(r'\textbf{neglected nonlinearity}')
        axes3.plot(t, psi, c='k')
        axes3.set_xlim(left=0, right=t[-1])
        axes3.set_xlabel(r'$t /s$')
        axes3.set_ylabel(r'$\psi$')
        if data['modules']['controller']['type'] == 'FController' or \
           data['modules']['controller']['type'] == 'JController':
               axes3.set_ylabel(r'$\theta /\frac{m}{s^2}$')
        if data['modules']['controller']['type'] == 'GController':
            axes3.set_ylabel(r'$\theta /\frac{m}{s^3}$')
        
        axes4 = fig.add_subplot(2, 2, 4)
        #axes4.set_title(r'\textbf{Beam Torque}')
        axes4.plot(t, tau, c='k')
        axes4.set_xlim(left=0, right=t[-1])
        axes4.set_xlabel(r'$t /s$')
        axes4.set_ylabel(r'$\tau /Nm$')
        
        # calculate epsilon_max
        start = 40
        end = 60
        indStart = t[0]
        indEnd = t[-1]
        for i in t:
            if i >= start:
                indStart = t.index(i)
            if i >= end:
                indEnd = t.index(i)
                break
        epsilon_max = max(eps[indStart:indEnd +1])
        
        
        #collect results
        output = {'epsilon_max': epsilon_max}
        output.update({'modules':data['modules']})

        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'HauserDiagrams')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(output))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')

        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}

