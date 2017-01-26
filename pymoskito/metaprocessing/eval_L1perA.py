# -*- coding: utf-8 -*-
import os

import matplotlib as mpl
import settings as st

mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.unicode'] = True
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from processing_gui import MetaProcessingModule


class eval_L1perA(MetaProcessingModule):
    '''
    create diagrams for evaluation of itea metric
    '''

    line_color = '#aaaaaa'
    line_style = '-'
    font_size = 20
    epsPercent = 2.5
    spacing = 0.01
    counter = 0

    def __init__(self):
        MetaProcessingModule.__init__(self)
        return

    def sortLists(self, val):
        val[1] = [x for (y, x) in sorted(zip(val[0], val[1]))]
        val[0] = sorted(val[0])
        return val

    def run(self, postResults):
        controller_dict = {"FController": [[], []],
                           "GController": [[], []],
                           "JController": [[], []],
                           "LSSController": [[], []],
                           "PIFeedbackController": [[], []]}

        # TODO: fill levels per input
        level1 = 'modules'
        level2 = 'trajectory'
        level3 = 'Amplitude'
        x_label = 'A [m]'
        y_label = 'E [m^2]'

        for elem in postResults:
            controller_dict[elem['modules']['controller']['type']][0].append(elem[level1][level2][level3])
            controller_dict[elem['modules']['controller']['type']][1].append(elem['metrics']['L1NormAbs'])

        fig = Figure()
        axes = fig.add_subplot(1, 1, 1)

        xMax = 0
        leg = []
        for elem in controller_dict:
            controller_dict[elem] = self.sortLists(controller_dict[elem])
            axes.plot(controller_dict[elem][0], controller_dict[elem][1], 'o-',
                      c=st.color_cycle[elem])
            leg.append(elem)
            if controller_dict[elem][0]:
                if xMax < controller_dict[elem][0][-1]:
                    xMax = controller_dict[elem][0][-1]
        axes.legend(leg, loc=0)
        axes.set_xlim(left=0.1, right=xMax)
        #        axes.set_ylim(top=6.0, bottom=3)
        axes.set_xlabel(r'$' + x_label + '$', size=st.label_size)
        axes.set_ylabel(r'$' + y_label + '$', size=st.label_size)
        axes.set_title(r'Fehlerintegral \"uber Amplitude', size=st.label_size)
        axes.grid(color='#ababab', linestyle='--')

        # write results
        filePath = os.path.join(os.path.pardir, 'results', 'metaprocessing', 'A2')
        if not os.path.isdir(filePath):
            os.makedirs(filePath)

        metaName = 'L1-plotA'
        fileName = os.path.join(filePath, metaName)
        canvas = FigureCanvas(fig)
        fig.savefig(fileName + '.svg')
        fig.savefig(fileName + '.png')
        fig.savefig(fileName + '.pdf')

        results = [{'figure': canvas, 'name': metaName}, \
                   ]

        return results
