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
        results = {}
        output = {}
        print 'processing ', data['regime name']
        
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
            
        error = np.subtract(yd, y[0])
        
        # controlleroutput is a torque
        tau = data['results']['controller_output.0']
        # u in the neglected nonlinearity is theta_dd
        u = np.true_divide(\
                np.subtract(\
                    np.subtract(\
                        tau,\
                        np.multiply(\
                            np.multiply(\
                                np.multiply(\
                                    2*st.M,\
                                    y[0]\
                                ),\
                                y[1]\
                            ),\
                            y[3]\
                        )\
                    ),\
                    np.multiply(\
                        st.M*st.G,\
                        np.multiply(\
                            y[0],\
                            np.cos(y[2])\
                        )\
                    )\
                ),\
                np.add(
                    np.multiply(\
                        st.M,\
                        np.power(y[0], 2)\
                    ),\
                    st.J + st.Jb\
                )\
            )

        # Parameter from Controller -> modelling (estimate/meausre paramters)
        # and then neglect psi therm
        # if you are interested in the error through the negligence 
        if data['modules']['controller']['type'] == 'FController':
            psi = np.multiply(np.multiply(st.B, y[0]), np.power(y[3],2))
        elif data['modules']['controller']['type'] == 'GController':
            psi = np.multiply(np.multiply(np.dot(2*st.B, y[0]), y[3]), u)
        elif data['modules']['controller']['type'] == 'JController':
            psi = np.multiply(np.multiply(np.multiply(st.B,y[0]), np.power(y[3], 2)),\
                       np.multiply(st.B*st.G, np.subtract(y[2], np.sin(y[2]))))
        else:
            # psi is not defined in this case
            psi = np.dot(0, t)

        # plots
        fig = Figure()
        fig.subplots_adjust(wspace=0.3, hspace=0.25)

        axes1 = fig.add_subplot(2, 2, 1)
        #axes1.set_title(r'\textbf{output error = yd - x0}')
        axes1.plot(t, error, c='k')
        axes1.set_xlim(left=0, right=t[-1])
        axes1.set_xlabel(r'$t \,[s]$', size=st.label_size)
        axes1.set_ylabel(r'$e \,[m]$', size=st.label_size)
        
        axes2 = fig.add_subplot(2, 2, 2)
        #axes2.set_title(r'\textbf{Beam Angle}')
        axes2.plot(t, y[2], c='k')
        axes2.set_xlim(left=0, right=t[-1])
        axes2.set_xlabel(r'$t \, [s]$', size=st.label_size)
        axes2.set_ylabel(r'$\theta \, [rad]$', size=st.label_size)
            
        axes3 = fig.add_subplot(2, 2, 3)
        #axes3.set_title(r'\textbf{neglected nonlinearity}')
        axes3.plot(t, psi, c='k')
        axes3.set_xlim(left=0, right=t[-1])
        axes3.set_xlabel(r'$t [s]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'FController':
            axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'JController':
            axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
        if data['modules']['controller']['type'] == 'GController':
            axes3.set_ylabel(r'$\psi_3 \, [\frac{m}{s^3}]$', size=st.label_size)
        
        axes4 = fig.add_subplot(2, 2, 4)
        #axes4.set_title(r'\textbf{Beam Torque}')
        axes4.plot(t, tau, c='k')
        axes4.set_xlim(left=0, right=t[-1])
        axes4.set_xlabel(r'$t \,[s]$', size=st.label_size)
        axes4.set_ylabel(r'$\tau \,[Nm]$', size=st.label_size)
        
        # calculate maximumError
        start = 30
        end = 40
        tStartIdx = next((idx for idx, x in enumerate(t) if x >= start), 0)
        tEndIdx = next((idx for idx, x in enumerate(t[start:]) if x >= end), len(t) - 1)

        maximumError = None
        if tStartIdx < tEndIdx:
            maximumError = max(error[tStartIdx:tEndIdx])        
        
        print 'maximum error between %d and %d seconds: %f' %\
                (start, end, maximumError)
        
        #collect results
        output.update({'maximumError': maximumError})

        #check for sim succes
        if not data['results']['finished']:
            for key in output.keys():
                output[key] = None


        results.update({'metrics': output})
        results.update({'modules':data['modules']})

        #write results
        filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'HauserDiagrams')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)
        
        fileName = os.path.join(filePath, data['regime name'])
        with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
            f.write(repr(results))

        canvas = FigureCanvas(fig)
        fig.savefig(fileName+'.svg')
        fig.savefig(fileName+'.png')

        return {'name':'_'.join([data['regime name'], self.name]),\
                    'figure': canvas}

