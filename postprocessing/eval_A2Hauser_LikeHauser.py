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

from postprocessor import PostProcessingModule
import settings as st

#define your own functions here
class eval_A2Hauser_LikeHauser(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    name = 'A2_hauser'

    def __init__(self):
        PostProcessingModule.__init__(self)
        return
        
    def process(self, files):
        print 'process() of A2Hauser_LikeHauser called'
        results = {}
        output = {}
        l = []
        
        controllerDict = {'FController':[],\
                          'GController':[],\
                          'JController':[]}
        for elem in controllerDict:
            controllerDict.update({elem:{'e':{},'theta':{}, 'psi':{}, 'tau':{}}})    
            for var in controllerDict[elem]:
                for i in range(1, 4, 1):           
                    controllerDict[elem][var].update({i:[[],[]]}) 

        for res in files:
                           
            #calculate datasets
            t = res['results']['simTime']               
                           
            yd = res['results']['trajectory_output.0']
            y = []
            for i in range(4):
                y.append(res['results']['model_output.'+str(i)]  )
                
            error = np.subtract(yd, y[0])
            
            # controlleroutput is a torque
            tau = res['results']['controller_output.0']
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
            if res['modules']['controller']['type'] == 'FController':
                psi = np.multiply(np.multiply(st.B, y[0]), np.power(y[3],2))
            elif res['modules']['controller']['type'] == 'GController':
                psi = np.multiply(np.multiply(np.dot(2*st.B, y[0]), y[3]), u)
            elif res['modules']['controller']['type'] == 'JController':
                psi = np.multiply(np.multiply(np.multiply(st.B,y[0]), np.power(y[3], 2)),\
                           np.multiply(st.B*st.G, np.subtract(y[2], np.sin(y[2]))))
            else:
                # psi is not defined in this case
                psi = np.dot(0, t)
            
            # Dict füllen
            level1 = res['modules']['controller']['type'] 
            level3 = res['modules']['trajectory']['Amplitude']
            
            #Zeit anhängen
#            controllerDict[level1].update({'t':t})
            controllerDict[level1]['e'][level3][0] = t
            controllerDict[level1]['theta'][level3][0] = t
            controllerDict[level1]['psi'][level3][0] = t
            controllerDict[level1]['tau'][level3][0] = t
#            # Werte anhängen           
            controllerDict[level1]['e'][level3][1] = error
            controllerDict[level1]['theta'][level3][1] = y[2]
            controllerDict[level1]['psi'][level3][1] = psi
            controllerDict[level1]['tau'][level3][1] = tau
            
            
        #Plots erzeugen
        contr = ['FController', 'GController', 'JController']
        for c in contr:
            print 'controller:', c
            
            fig = Figure()
#            fig.subplots_adjust(wspace=0.3, hspace=0.25) 
            fig.subplots_adjust(wspace=0.6, hspace=0.6) 
            fig.suptitle(r'\textbf{' + c + '}', size=st.title_size)
            
            for i in range(1, 4, 1):
                axes1 = fig.add_subplot(2, 2, 1)       
                axes1.set_title(r'\textbf{output error = yd - x0}', size=st.label_size)
                axes1.plot(controllerDict[c]['e'][i][0], controllerDict[c]['e'][i][1])
                axes1.set_xlim(left=0, right=controllerDict[c]['e'][1][0][-1])
                axes1.set_xlabel(r'$t \,[s]$', size=st.label_size)
                axes1.set_ylabel(r'$e \,[m]$', size=st.label_size)
                
                axes2 = fig.add_subplot(2, 2, 2)
                axes2.set_title(r'\textbf{Beam Angle}', size=st.label_size)
                axes2.plot(controllerDict[c]['theta'][i][0], controllerDict[c]['theta'][i][1])
                axes2.set_xlim(left=0, right=controllerDict[c]['theta'][1][0][-1])
                axes2.set_xlabel(r'$t \, [s]$', size=st.label_size)
                axes2.set_ylabel(r'$\theta \, [rad]$', size=st.label_size)
                    
                axes3 = fig.add_subplot(2, 2, 3)
                axes3.set_title(r'\textbf{neglected nonlinearity}', size=st.label_size)
                axes3.plot(controllerDict[c]['psi'][i][0], controllerDict[c]['psi'][i][1])
                axes3.set_xlim(left=0, right=controllerDict[c]['psi'][1][0][-1])
                axes3.set_xlabel(r'$t [s]$', size=st.label_size)
                if res['modules']['controller']['type'] == 'FController':
                    axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
                if res['modules']['controller']['type'] == 'JController':
                    axes3.set_ylabel(r'$\psi_2 \, [\frac{m}{s^2}]$', size=st.label_size)
    #                axes3.set_ylim(top = 0.6, bottom = -0.6)
                if res['modules']['controller']['type'] == 'GController':
                    axes3.set_ylabel(r'$\psi_3 \, [\frac{m}{s^3}]$', size=st.label_size)
                
                axes4 = fig.add_subplot(2, 2, 4)
                axes4.set_title(r'\textbf{Beam Torque}', size=st.label_size)
                axes4.plot(controllerDict[c]['tau'][i][0], controllerDict[c]['tau'][i][1])
                axes4.set_xlim(left=0, right=controllerDict[c]['tau'][1][0][-1])
                axes4.set_xlabel(r'$t \,[s]$', size=st.label_size)
                axes4.set_ylabel(r'$\tau \,[Nm]$', size=st.label_size)
                
                # calculate maximumError
                start = 30
                end = 40
                tStartIdx = next((idx for idx, x in enumerate(controllerDict[c]['e'][i][0]) if x >= start), 0)
                tEndIdx = next((idx for idx, x in enumerate(controllerDict[c]['e'][i][0][start:]) if x >= end),\
                                len(controllerDict[c]['e'][i][0]) - 1)
                
                maximumError = None
                if tStartIdx < tEndIdx:
                    maximumError = max(controllerDict[c]['e'][i][1][tStartIdx:tEndIdx])        
                
                print 'maximum error between %d and %d seconds: %f' %\
                        (start, end, maximumError)
                    
            #check for sim succes
            if not res['results']['finished']:
                for key in output.keys():
                    output[key] = None
    
    
            results.update({'metrics': output})
            results.update({'modules':res['modules']})
    
            #write results
            filePath = os.path.join(os.path.pardir, 'results', 'postprocessing', 'HauserDiagramsLikeHauser')
            if not os.path.isdir(filePath):
                os.makedirs(filePath)
            
            fileName = os.path.join(filePath, c)#res['regime name'])
            with open(fileName+'.pof', 'w') as f: #POF - Postprocessing Output File
                f.write(repr(results))
    
            canvas = FigureCanvas(fig)
            fig.savefig(fileName+'.svg')
            fig.savefig(fileName+'.png')
            fig.savefig(fileName+'.pdf')
    
#            l.append({'name':'_'.join([res['regime name'], self.name]),\
#                        'figure': canvas})
            l.append({'name':'_'.join([c, self.name]),\
                        'figure': canvas})
        
        return l
        
        
        
        


