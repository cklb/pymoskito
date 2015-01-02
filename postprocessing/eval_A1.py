# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp

import matplotlib
matplotlib.use("Qt4Agg")
#from matplotlib.backends import qt4_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D as line

from postprocessing import PostProcessingModule

#define your own functions here
class eval_A1(PostProcessingModule):
    '''
    create diagrams for evaluation step A1
    '''

    line_color = '#aaaaaa'

    def __init__(self):
        PostProcessingModule.__init__(self)
        return

    def run(self, data):
        fig = Figure()
        canvas = FigureCanvas(fig)
        epsPercent = 2.5

        #calculate datasets
        t = data['results']['simTime']
        y = data['results']['model_output.0']
        yd = data['results']['trajectory_output.0'][-1]

        #calc attack-time
        ta = t[y.index([x for x in y if x > yd*0.9][0])]
        attackLine = line([ta, ta], [0, y[t.index(ta)]], ls='--', c=self.line_color)

        #calc rise-time
        tr = t[y.index([x for x in y if x > yd][0])]
        riseLine = line([tr, tr], [0, y[t.index(tr)]], ls='--', c=self.line_color)

        #calc overshoot time
        lastval = 0
        for val in y[t.index(tr):]:
            if val < lastval:
                break
            else:
                lastval = val

        to = t[y.index(val)]
        do = val - yd
        doPercent = do/yd * 100
        overLine = line([to, to], [0, y[t.index(to)]], ls='--', c=self.line_color)

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
        dampLine = line([td, td], [0, y[t.index(td)]], ls='--', c=self.line_color)

        #calc stationary deviation
        ys = y[-1] - yd

        axes = fig.add_subplot(111)
        axes.set_title=(r'\textbf{Sprungantwort}')
        axes.set_xlabel=('test') #r'\textit{Zeit [s]}')
        axes.set_ylabel=(r'\textit{Ballposition r(t) [m]}')
        axes.plot(t, y, c='k')
        axes.add_line(attackLine)
        axes.add_line(riseLine)
        axes.add_line(overLine)
        axes.add_line(dampLine)

        positions = [ta, tr, to, td]
        names = [r'$T_r$', r'$T_a$', r'$T_m$', r'$T_{\epsilon}$']

        for idx, name in enumerate(names):
            axes.text(positions[idx], .1, name)

        fig.savefig('test.svg')

        return canvas
