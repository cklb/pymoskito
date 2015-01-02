# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp

from PyQt4 import QtCore
import pyqtgraph as pg

from postprocessing import PostProcessingModule

#define your own functions here
class eval_A1(PostProcessingModule):
    '''
    create diagrams for evaluation step A1
    '''

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        epsPercent = 2.5

        #calculate datasets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        #calc rise-time
        tr = t[y.index([x for x in y if x > yd*0.9][0])]
        print 'tr: ', tr

        #calc control-time
        tc = t[y.index([x for x in y if x > yd][0])]
        print 'tc: ', tc

        #calc overshoot time
        lastval = 0
        for val in y[t.index(tc):]:
            if val < lastval:
                break
            else:
                lastval = val

        to = t[y.index(val)]
        do = val - yd
        doPercent = do/yd * 100

        #calc damping-time
        eps = epsPercent*yd/100
        enterIdx = -1
        for idx, val in enumerate(y):
            if enterIdx == -1:
                if abs(val - yd) < eps:
                    enterIdx = idx
            else:
                if abs(val - yd) >= eps:
                    enterIdx = -1
        
        td = t[enterIdx]

        #calc stationary deviation
        ys = y[-1] - yd

        plots = pg.GraphicsLayoutWidget()
        plots.setBackground(background=None)
        linePen = pg.mkPen('#888888', width=1.0, style=QtCore.Qt.DashLine)
        fgPen = pg.mkPen('#000000', width=1, style=QtCore.Qt.SolidLine)
        thickPen = pg.mkPen('#000000', width=1.5, style=QtCore.Qt.SolidLine)

        p1 = pg.PlotItem(title='Sprungantwort', labels={'left': 'yd', 'bottom':'t'})
        p1.getAxis('left').setPen(fgPen)
        p1.getAxis('bottom').setPen(fgPen)
        p1.plot(t, y, pen=thickPen)
        #p1.showGrid(x=True, y=True, alpha=0.9)

        p1.addLine(y=yd, movable=False, pen=thickPen)
        p1.addLine(y=yd+eps, movable=False, pen=linePen)
        p1.addLine(y=yd-eps, movable=False, pen=linePen)
        p1.addLine(x=tr, movable=False, pen=linePen)
        p1.addLine(x=tc, movable=False, pen=linePen)
        p1.addLine(x=to, movable=False, pen=linePen)
        p1.addLine(x=td, movable=False, pen=linePen)
        plots.addItem(p1, 0, 0)


        #exporter = pg.exporters.ImageExporter.ImageExporter(p1)
        #exporter.parameters()['width'] = 500
        #exporter.parameters()['height'] = 500
        #exporter.export('test.png')

        return plots
