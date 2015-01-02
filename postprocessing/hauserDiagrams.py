# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp

import pyqtgraph as pg

from postprocessing import PostProcessingModule

#define your own functions here
class hauserDiagrams(PostProcessingModule):
    '''
    create diagrams like hauser did
    '''

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        #calculate datasets
        t = data['results']['simTime']
        yd = data['results']['trajectory_output.0']
        y = []
        for i in range(3):
            y.append(data['results']['model_output.'+str(i)]  )

        vDiff = np.vectorize(self.diff)
        eps = vDiff(yd[0], y[0])

        #TODO phi one to three


        plots = pg.GraphicsLayoutWidget()
        p1 = pg.PlotItem(name='Sollwertfehler', lables={'left': 'epsilon', 'bottom':'t'})
        p1.plot(t, eps)
        p2 = pg.PlotItem(name='Sollwertfehler', lables={'left': 'epsilon', 'bottom':'t'})
        p2.plot(t, eps)


        plots.addItem(p1, 0, 0)
        plots.addItem(p2, 1, 0)

        return plots
