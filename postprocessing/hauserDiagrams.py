# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp

import pyqtgraph as pg

from postprocessing import PostProcessingModule
import settings as st

#define your own functions here
class hauserDiagrams(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        
        # vectorise skalar functions
        vSubt = np.vectorize(self.subt)
        vMul = np.vectorize(self.mul)
        vAdd = np.vectorize(self.add)
          
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(4):
            y.append(data['results']['model_output.'+str(i)]  )
            
        eps = vSubt(yd[0], y[0])

        #TODO phi one to three
        #FIXME: durchdenke welches u gemeint ist: u=tau oder u = u
        u = data['results']['controller_output.0']
        
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
                       np.dot(B*G, vSubt(y[2] - np.sin(y[2]))))
        else:
            raise Exception('psi is useless')
            psi = np.dot(0, t)

        plots = pg.GraphicsLayoutWidget()
        p1 = pg.PlotItem(name='Sollwertfehler', lables={'left': 'epsilon', 'bottom':'t'})
        p1.plot(t, eps)
        
        p2 = pg.PlotItem(name='Theta', lables={'left': 'Theta', 'bottom':'t'})
        p2.plot(t, y[2])
        
        p3 = pg.PlotItem(name='Psi - neglected nonlinearity', lables={'left': 'Psi', 'bottom':'t'})
        p3.plot(t, psi)
        
        p4 = pg.PlotItem(name='Tau', lables={'left': 'Tau', 'bottom':'t'})
        p4.plot(t, data['results']['controller_output.0'])


        plots.addItem(p1, 0, 0)
        plots.addItem(p2, 0, 1)
        plots.addItem(p3, 1, 0)
        plots.addItem(p4, 1, 1)

        return plots




